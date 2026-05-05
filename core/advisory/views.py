"""
Views for the advisory app.
"""

# django_packages
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# other_apps_packages
from core.profiles.decorators import agent_required

# app_packages
from .forms import AdvisoryPostForm
from .models import AdvisoryPost


@login_required
def advisory_post_list_view(request):
    """
    Display all published advisory posts on the platform.

    Accessible to any authenticated user. Agents also see their own
    unpublished drafts inline via my_advisory_posts_view instead.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered advisory post list page.
    """
    posts = AdvisoryPost.objects.filter(is_published=True).select_related(
        "author__user"
    )

    return render(
        request=request,
        template_name="advisory/pages/advisory_post_list_page.html",
        context={"posts": posts},
    )


@agent_required
def my_advisory_posts_view(request):
    """
    Display all advisory posts authored by the authenticated agent,
    including unpublished drafts.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered agent post list page.
    """

    posts = AdvisoryPost.objects.filter(
        author=request.user.agent_profile
    ).select_related("author__user")

    return render(
        request=request,
        template_name="advisory/pages/my_advisory_posts_page.html",
        context={"posts": posts},
    )


@agent_required
def create_advisory_post_view(request):
    """
    Allow an extension agent to create a new advisory post.

    GET  — renders an empty form.
    POST — validates and saves the post as a draft, then redirects to the
           detail page. The agent can publish from there separately.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.

    Returns
    -------
    HttpResponse
        Rendered create page or redirect to the post detail page.
    """

    if request.method == "POST":
        form = AdvisoryPostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.agent_profile

            publish = request.POST.get("publish") == "true"

            if publish:
                post.is_published = True
                post.published_at = timezone.now()

            post.save()
            form.save_m2m()

            raw_tags = form.cleaned_data.get("tags", "")
            tag_names = [t.strip() for t in raw_tags.split(",") if t.strip()]
            post.tags.set(tag_names)

            messages.success(
                request,
                (
                    "Post published successfully."
                    if publish
                    else "Draft saved successfully."
                ),
            )
            return redirect("advisory:post_detail", post_id=post.pk)
    else:
        form = AdvisoryPostForm()

    return render(
        request=request,
        template_name="advisory/pages/create_post_page.html",
        context={"form": form},
    )


@agent_required
def edit_advisory_post_view(request, post_id):
    """
    Allow an extension agent to edit one of their own advisory posts.

    GET  — renders the form pre-filled with existing data.
    POST — validates and saves updates, then redirects to the detail page.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    post_id : int
        The primary key of the post to edit.

    Returns
    -------
    HttpResponse
        Rendered edit page or redirect to the post detail page.
    """

    post = get_object_or_404(
        AdvisoryPost,
        pk=post_id,
        author=request.user.agent_profile,
    )

    if request.method == "POST":
        form = AdvisoryPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)

            publish = request.POST.get("publish") == "true"
            if publish and not updated_post.is_published:
                updated_post.is_published = True
                # django_packages
                from django.utils import timezone

                if not updated_post.published_at:
                    updated_post.published_at = timezone.now()

            updated_post.save()
            form.save_m2m()

            # Save taggit tags explicitly after the post has a PK
            raw_tags = form.cleaned_data.get("tags", "")
            post.tags.set(raw_tags)

            messages.success(request, "Post updated successfully.")

            return redirect("advisory:post_detail", post_id=post.pk)
    else:
        form = AdvisoryPostForm(instance=post)

    return render(
        request=request,
        template_name="advisory/pages/edit_post_page.html",
        context={"form": form, "post": post},
    )


@login_required
def advisory_post_detail_view(request, post_id):
    """
    Display a single advisory post.

    Published posts are visible to any authenticated user. An agent may
    also view their own unpublished drafts — no one else can.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    post_id : int
        The primary key of the post to display.

    Returns
    -------
    HttpResponse
        Rendered post detail page.
    """

    post = get_object_or_404(
        AdvisoryPost.objects.select_related("author__user"),
        pk=post_id,
    )

    # Block access to unpublished posts unless the requesting user is the author.
    if not post.is_published:
        if not request.user.is_agent or post.author.user != request.user:
            # django_packages
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied

    return render(
        request=request,
        template_name="advisory/pages/advisory_post_detail_page.html",
        context={"post": post},
    )


@agent_required
def publish_post_view(request, post_id):
    """
    Publish a draft advisory post.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    post_id : int
        The primary key of the post to display.

    Returns
    -------
    HttpResponseRedirect
        Redirects back to the advisory post detail page after publishing.
    """

    post = get_object_or_404(
        AdvisoryPost,
        pk=post_id,
        author=request.user.agent_profile,
    )
    post.publish()

    messages.success(
        request=request,
        message="Post published successfully.",
    )

    return redirect("advisory:post_detail", post_id=post.pk)


@agent_required
def unpublish_post_view(request, post_id):
    """
    Revert a published advisory post back to draft.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    post_id : int
        The primary key of the post to display.

    Returns
    -------
    HttpResponseRedirect
        Redirects back to the advisory post detail page after publishing.
    """

    post = get_object_or_404(
        AdvisoryPost,
        pk=post_id,
        author=request.user.agent_profile,
    )
    post.unpublish()

    messages.success(
        request=request,
        message="Post unpublished and returned to drafts.",
    )

    return redirect("advisory:post_detail", post_id=post.pk)


@agent_required
def delete_advisory_post_view(request, post_id):
    """
    Delete an unpublished advisory post owned by the authenticated agent.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request.
    post_id : int
        The primary key of the post to display.

    Returns
    -------
    HttpResponseRedirect
        Redirects back to the advisory post detail page after publishing.
    """

    post = get_object_or_404(
        AdvisoryPost,
        pk=post_id,
        author=request.user.agent_profile,
    )

    # 🚫 HARD RULE: only drafts can be deleted
    if post.is_published:
        raise PermissionDenied("Published posts cannot be deleted.")

    if request.method == "POST":
        post.delete()
        messages.success(request, "Draft deleted successfully.")
        return redirect("advisory:my_posts")

    return redirect("advisory:post_detail", post_id=post.pk)
