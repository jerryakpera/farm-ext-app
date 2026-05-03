"""
Views for the `questions` app.
"""

# django_packages
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

# other_apps_packages
from core.profiles.decorators import farmer_required

# app_packages
from .forms import AskQuestionForm
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


@farmer_required
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


@farmer_required
def question_detail_view(request, question_id):
    """
    Display a single question and all its answers.

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
    question = get_object_or_404(
        Question.objects.select_related(
            "crop_concern",
            "farm",
        ).prefetch_related(
            "answers__agent__user",
            "answers__images",
            "answers__helpfulness_ratings",
        ),
        pk=question_id,
        farmer=request.user.farmer_profile,
    )

    return render(
        request=request,
        template_name="questions/pages/question_detail_page.html",
        context={"question": question},
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
