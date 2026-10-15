from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
import datetime
from .models import Book, BookIssue
from .forms import BookForm, BookIssueForm, BookReturnForm


def book_list(request):
    """Catalog of library books with search and category filters"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    stock_status = request.GET.get('stock', '').strip()

    books = Book.objects.all()

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query))
    if category:
        books = books.filter(category=category)
    if stock_status == 'available':
        books = books.filter(available_copies__gt=0)
    elif stock_status == 'out_of_stock':
        books = books.filter(available_copies=0)

    total_titles = Book.objects.count()
    total_copies = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    total_available = Book.objects.aggregate(total=Sum('available_copies'))['total'] or 0
    active_loans = BookIssue.objects.filter(status='Issued').count()
    overdue_loans = sum(1 for bi in BookIssue.objects.filter(status='Issued') if bi.is_currently_overdue)

    context = {
        'page_title': 'Library & Catalog',
        'active_tab': 'library_books',
        'books': books,
        'query': query,
        'category_filter': category,
        'stock_filter': stock_status,
        'categories': Book.CATEGORY_CHOICES,
        'total_titles': total_titles,
        'total_copies': total_copies,
        'total_available': total_available,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
    }
    return render(request, 'library/book_list.html', context)


def book_add(request):
    """Add a book to catalog"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" added to library!')
            return redirect('library:book_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm()

    return render(request, 'library/book_form.html', {
        'form': form,
        'page_title': 'Add Library Book',
        'active_tab': 'library_books',
        'action': 'Add',
    })


def book_edit(request, pk):
    """Edit book details"""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('library:book_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm(instance=book)

    return render(request, 'library/book_form.html', {
        'form': form,
        'book': book,
        'page_title': f'Edit {book.title}',
        'active_tab': 'library_books',
        'action': 'Edit',
    })


def book_delete(request, pk):
    """Delete book"""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" deleted from catalog.')
        return redirect('library:book_list')

    return render(request, 'library/book_confirm_delete.html', {
        'book': book,
        'page_title': 'Delete Book',
        'active_tab': 'library_books',
    })


def book_issue_list(request):
    """Track all issued books, returns, and overdue borrowings"""
    status_filter = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()

    issues = BookIssue.objects.select_related('book', 'student', 'teacher').all()

    if status_filter:
        issues = issues.filter(status=status_filter)
    if query:
        issues = issues.filter(
            Q(book__title__icontains=query) |
            Q(student__student_name__icontains=query) |
            Q(teacher__full_name__icontains=query) |
            Q(book__isbn__icontains=query)
        )

    # Check and flag overdue status
    for item in issues:
        if item.status == 'Issued' and item.is_currently_overdue:
            item.computed_fine = item.calculate_fine()
        else:
            item.computed_fine = item.fine_amount

    context = {
        'page_title': 'Book Loans & Returns',
        'active_tab': 'library_issues',
        'issues': issues,
        'status_filter': status_filter,
        'query': query,
        'statuses': BookIssue.STATUS_CHOICES,
    }
    return render(request, 'library/issue_list.html', context)


def book_issue_create(request):
    """Issue a book to student or teacher"""
    prefill_book = request.GET.get('book', '')
    initial = {}
    if prefill_book:
        initial['book'] = prefill_book
    initial['due_date'] = datetime.date.today() + datetime.timedelta(days=14)

    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            book = issue.book
            if book.available_copies <= 0:
                messages.error(request, f'Sorry, no copies of "{book.title}" are currently available in the library.')
            else:
                book.available_copies -= 1
                book.save()
                issue.save()
                messages.success(request, f'"{book.title}" successfully issued to {issue.borrower_name}!')
                return redirect('library:book_issue_list')
        else:
            messages.error(request, 'Please correct the loan record errors below.')
    else:
        form = BookIssueForm(initial=initial)

    return render(request, 'library/issue_form.html', {
        'form': form,
        'page_title': 'Issue Book',
        'active_tab': 'library_issues',
    })


def book_return_action(request, pk):
    """Process book return, calculate fine, and restore available copies"""
    issue = get_object_or_404(BookIssue, pk=pk)
    today = datetime.date.today()
    suggested_fine = issue.calculate_fine()

    if request.method == 'POST':
        form = BookReturnForm(request.POST)
        if form.is_valid():
            ret_date = form.cleaned_data['return_date']
            fine = form.cleaned_data['fine_amount'] or Decimal('0.00')
            rmk = form.cleaned_data['remarks']

            issue.return_date = ret_date
            issue.fine_amount = fine
            issue.status = 'Returned'
            if rmk:
                issue.remarks = f"{issue.remarks} | Return: {rmk}" if issue.remarks else rmk
            issue.save()

            # Restore book copy
            book = issue.book
            if book.available_copies < book.total_copies:
                book.available_copies += 1
                book.save()

            messages.success(request, f'Book "{book.title}" successfully returned! (Fine collected: PKR {fine})')
            return redirect('library:book_issue_list')
    else:
        form = BookReturnForm(initial={'return_date': today, 'fine_amount': suggested_fine})

    return render(request, 'library/return_form.html', {
        'issue': issue,
        'form': form,
        'suggested_fine': suggested_fine,
        'page_title': f'Return {issue.book.title}',
        'active_tab': 'library_issues',
    })


def book_issue_delete(request, pk):
    """Delete loan record"""
    issue = get_object_or_404(BookIssue, pk=pk)
    if request.method == 'POST':
        # If deleted while still issued, restore book copy count
        if issue.status == 'Issued':
            book = issue.book
            if book.available_copies < book.total_copies:
                book.available_copies += 1
                book.save()
        issue.delete()
        messages.success(request, 'Book loan record removed.')
        return redirect('library:book_issue_list')

    return render(request, 'library/issue_confirm_delete.html', {
        'issue': issue,
        'page_title': 'Delete Loan Record',
        'active_tab': 'library_issues',
    })
