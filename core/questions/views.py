"""
Views for the `questions` app.
"""

# django_packages
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

# other_apps_packages
from core.custom_user.models import User
from core.profiles.decorators import agent_required, farmer_required

# app_packages
from .forms import AnswerQuestionForm, AskQuestionForm
from .models import Question


@farmer_required  # reuse the same decorator you already have in core.farms.views
def ask_question_view(request):
    """
    Allow a farmer to submit a new question.

    GET  — renders an empty form.
    POST — validates, saves the question and its images, then redirects.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered question form or redirect to the question detail page.
    """
    farmer = request.user.farmer_profile

    if request.method == "POST":
        form = AskQuestionForm(request.POST, request.FILES, farmer=farmer)
        if form.is_valid():
            question = form.save(farmer=farmer)
            messages.success(request, "Your question has been submitted.")
            return redirect("questions:question_detail", question_id=question.pk)
    else:
        form = AskQuestionForm(farmer=farmer)

    return render(
        request=request,
        template_name="questions/pages/ask_question_page.html",
        context={"form": form},
    )


@login_required
def question_list_view(request):
    """
    Display all questions submitted by the authenticated farmer.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered question list page.
    """

    questions = (
        Question.objects.all()
        .select_related("crop_concern", "farm", "farmer__user")
        .prefetch_related("answers")
    )

    context = {
        "questions": questions,
    }

    return render(
        request=request,
        context=context,
        template_name="questions/pages/question_list_page.html",
    )


@farmer_required
def my_question_list_view(request):
    """
    Display all questions submitted by the authenticated farmer.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered question list page.
    """

    questions = (
        Question.objects.filter(farmer=request.user.farmer_profile)
        .select_related("crop_concern", "farm")
        .prefetch_related("answers")
    )

    context = {"questions": questions}

    return render(
        request=request,
        context=context,
        template_name="questions/pages/question_list_page.html",
    )


@login_required
def question_detail_view(request, question_id):
    """
    Display a single question and all its answers.

    Each answer is annotated with helpful/not-helpful counts and,
    for authenticated farmers, their own rating if they have submitted one.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    question_id : int
        The primary key of the question to display.

    Returns
    -------
    HttpResponse
        Rendered question detail page.
    """
    # django_packages
    from django.db.models import Count, Q

    question = get_object_or_404(
        Question.objects.select_related(
            "crop_concern",
            "farm",
            "farmer__user",
        ),
        pk=question_id,
    )

    answers = list(
        question.answers.select_related("agent__user").annotate(
            helpful_count=Count(
                "helpfulness_ratings",
                filter=Q(helpfulness_ratings__is_helpful=True),
            ),
            not_helpful_count=Count(
                "helpfulness_ratings",
                filter=Q(helpfulness_ratings__is_helpful=False),
            ),
        )
    )

    if request.user.is_farmer:
        # app_packages
        from .models import AnswerHelpfulness

        farmer = request.user.farmer_profile
        ratings = AnswerHelpfulness.objects.filter(
            answer__in=answers,
            farmer=farmer,
        ).values("answer_id", "is_helpful")

        rating_map = {r["answer_id"]: r["is_helpful"] for r in ratings}

        for answer in answers:
            answer.user_rating = rating_map.get(answer.pk)
    else:
        for answer in answers:
            answer.user_rating = None

    return render(
        request=request,
        template_name="questions/pages/question_detail_page.html",
        context={"question": question, "answers": answers},
    )


@farmer_required
def edit_question_view(request, question_id):
    """
    Allow a farmer to edit their own question.

    Only open questions may be edited — once an agent has answered or
    escalated the question it should be considered locked.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    question_id : int
        The primary key of the question to edit.

    Returns
    -------
    HttpResponse
        Rendered edit form or redirect to the question detail page.
    """
    question = get_object_or_404(
        Question,
        pk=question_id,
        farmer=request.user.farmer_profile,
    )

    if question.status != Question.Status.OPEN:
        messages.error(
            request,
            "Only open questions can be edited.",
        )

        return redirect("questions:question_detail", question_id=question.pk)

    farmer = request.user.farmer_profile

    if request.method == "POST":
        form = AskQuestionForm(
            request.POST, request.FILES, instance=question, farmer=farmer
        )
        if form.is_valid():
            form.save(farmer=farmer)
            messages.success(request, "Your question has been updated.")

            return redirect("questions:question_detail", question_id=question.pk)
    else:
        form = AskQuestionForm(instance=question, farmer=farmer)

    return render(
        request=request,
        template_name="questions/pages/edit_question_page.html",
        context={"form": form, "question": question},
    )


@farmer_required
def delete_question_view(request, question_id):
    """
    Delete a farmer's own open question.

    Only POST is accepted. Questions that are no longer open cannot
    be deleted.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    question_id : int
        The primary key of the question to delete.

    Returns
    -------
    HttpResponse
        Redirect to the question list.
    """
    question = get_object_or_404(
        Question,
        pk=question_id,
        farmer=request.user.farmer_profile,
    )

    if question.status != Question.Status.OPEN:
        messages.error(request, "Only open questions can be deleted.")
        return redirect("questions:question_detail", question_id=question.pk)

    if request.method == "POST":
        question.delete()
        messages.success(request, "Your question has been deleted.")

    return redirect("questions:question_list")


@agent_required
def answer_question_view(request, question_id):
    """
    Allow an extension agent to post an answer to a farmer's question.

    GET  — renders the question alongside an empty answer form.
    POST — validates and saves the answer, then updates the question
           status to ANSWERED and redirects back to the same page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    question_id : int
        The primary key of the question being answered.

    Returns
    -------
    HttpResponse
        Rendered answer page or redirect back to the same view on success.
    """
    question = get_object_or_404(
        Question.objects.select_related(
            "farmer__user", "crop_concern", "farm"
        ).prefetch_related("answers__agent__user"),
        pk=question_id,
    )

    if request.method == "POST":
        form = AnswerQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.agent = request.user.agent_profile
            answer.save()

            if question.status == Question.Status.OPEN:
                question.status = Question.Status.ANSWERED
                question.save(update_fields=["status"])

            messages.success(request, "Your answer has been posted.")
            return redirect("questions:answer_question", question_id=question.pk)
    else:
        form = AnswerQuestionForm()

    return render(
        request=request,
        template_name="questions/pages/answer_question_page.html",
        context={"question": question, "form": form},
    )


@farmer_required
def rate_answer_view(request, answer_id):
    """
    Record a farmer's helpfulness rating on an answer.

    Only POST is accepted. A farmer may only rate an answer once —
    subsequent submissions update the existing rating rather than
    creating a duplicate, since AnswerHelpfulness has a unique_together
    constraint on (answer, farmer).

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    answer_id : int
        The primary key of the answer being rated.

    Returns
    -------
    HttpResponse
        Redirect back to the question detail page.
    """
    # app_packages
    from .models import Answer, AnswerHelpfulness

    if request.method != "POST":
        return redirect("questions:question_list")

    answer = get_object_or_404(Answer, pk=answer_id)
    farmer = request.user.farmer_profile
    is_helpful = request.POST.get("is_helpful") == "true"

    AnswerHelpfulness.objects.update_or_create(
        answer=answer,
        farmer=farmer,
        defaults={"is_helpful": is_helpful},
    )

    messages.success(
        request=request,
        message=(
            "Thank you for your feedback."
            if is_helpful
            else "Thanks for letting us know."
        ),
    )

    return redirect(
        "questions:question_detail",
        question_id=answer.question.pk,
    )
