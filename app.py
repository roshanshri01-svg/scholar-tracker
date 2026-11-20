from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from datetime import date
import database

app = Flask(__name__)
app.secret_key = "scholar-track-secure-secret-key-2026"


# Jinja custom filter for formatting currency
@app.template_filter("currency")
def currency_filter(val):
    try:
        amount = float(val)
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


# Inject today's date and utility info into all templates
@app.context_processor
def inject_globals():
    return {
        "today_str": date.today().strftime("%Y-%m-%d"),
        "today_display": date.today().strftime("%B %d, %Y"),
    }


@app.route("/")
@app.route("/dashboard")
def dashboard():
    """Render the main dashboard with metrics, upcoming deadlines, and recent entries."""
    stats = database.get_dashboard_data()
    return render_template("index.html", stats=stats, active_page="dashboard")


@app.route("/scholarships")
def scholarships_list():
    """Render the scholarship directory with search, filter, and sort capabilities."""
    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "All")
    deadline_filter = request.args.get("deadline", "all")
    sort_by = request.args.get("sort", "deadline_asc")

    scholarships = database.get_all_scholarships(
        search=search_query if search_query else None,
        status=status_filter if status_filter else None,
        deadline_type=deadline_filter,
        sort_by=sort_by,
    )

    return render_template(
        "scholarships.html",
        scholarships=scholarships,
        search_query=search_query,
        status_filter=status_filter,
        deadline_filter=deadline_filter,
        sort_by=sort_by,
        active_page="scholarships",
    )


@app.route("/scholarships/add", methods=["GET", "POST"])
def add_scholarship():
    """Handle adding a new scholarship."""
    if request.method == "POST":
        name = request.form.get("scholarship_name", "").strip()
        provider = request.form.get("provider", "").strip()
        description = request.form.get("description", "").strip()
        eligibility = request.form.get("eligibility", "").strip()
        amount_raw = request.form.get("amount", "").strip()
        deadline = request.form.get("deadline", "").strip()
        application_link = request.form.get("application_link", "").strip()
        status = request.form.get("application_status", "Pending").strip()

        # Input Validations
        errors = []
        if not name:
            errors.append("Scholarship Name is required.")
        if not provider:
            errors.append("Provider/Organization is required.")
        if not deadline:
            errors.append("Application Deadline is required.")
        else:
            try:
                date.fromisoformat(deadline)
            except ValueError:
                errors.append("Invalid date format for Deadline. Please use YYYY-MM-DD.")

        # Amount validation
        amount = 0.0
        if amount_raw:
            try:
                # Remove dollar sign and commas if entered by user
                clean_amount = amount_raw.replace("$", "").replace(",", "")
                amount = float(clean_amount)
                if amount < 0:
                    errors.append("Scholarship amount cannot be negative.")
            except ValueError:
                errors.append("Please enter a valid numeric value for Amount.")

        valid_statuses = ["Pending", "Applied", "Approved", "Rejected"]
        if status not in valid_statuses:
            status = "Pending"

        if errors:
            for error in errors:
                flash(error, "danger")
            # Preserve user input in the form
            form_data = {
                "scholarship_name": name,
                "provider": provider,
                "description": description,
                "eligibility": eligibility,
                "amount": amount_raw,
                "deadline": deadline,
                "application_link": application_link,
                "application_status": status,
            }
            return render_template("add_scholarship.html", form_data=form_data, active_page="add_scholarship")

        try:
            new_id = database.add_scholarship(
                name=name,
                provider=provider,
                description=description,
                eligibility=eligibility,
                amount=amount,
                deadline=deadline,
                link=application_link,
                status=status,
            )
            flash(f"Scholarship '{name}' was added successfully!", "success")
            return redirect(url_for("scholarship_detail", id=new_id))
        except Exception as e:
            flash(f"Error saving scholarship to database: {str(e)}", "danger")
            return render_template("add_scholarship.html", form_data=request.form, active_page="add_scholarship")

    return render_template("add_scholarship.html", form_data={}, active_page="add_scholarship")


@app.route("/scholarships/<int:id>")
def scholarship_detail(id):
    """Display comprehensive details for a specific scholarship."""
    scholarship = database.get_scholarship_by_id(id)
    if not scholarship:
        flash("Scholarship not found.", "warning")
        return redirect(url_for("scholarships_list"))

    return render_template("scholarship_details.html", scholarship=scholarship, active_page="scholarships")


@app.route("/scholarships/<int:id>/edit", methods=["GET", "POST"])
def edit_scholarship(id):
    """Handle editing an existing scholarship."""
    scholarship = database.get_scholarship_by_id(id)
    if not scholarship:
        flash("Scholarship not found.", "warning")
        return redirect(url_for("scholarships_list"))

    if request.method == "POST":
        name = request.form.get("scholarship_name", "").strip()
        provider = request.form.get("provider", "").strip()
        description = request.form.get("description", "").strip()
        eligibility = request.form.get("eligibility", "").strip()
        amount_raw = request.form.get("amount", "").strip()
        deadline = request.form.get("deadline", "").strip()
        application_link = request.form.get("application_link", "").strip()
        status = request.form.get("application_status", "Pending").strip()

        errors = []
        if not name:
            errors.append("Scholarship Name is required.")
        if not provider:
            errors.append("Provider is required.")
        if not deadline:
            errors.append("Deadline is required.")
        else:
            try:
                date.fromisoformat(deadline)
            except ValueError:
                errors.append("Invalid date format for Deadline.")

        amount = 0.0
        if amount_raw:
            try:
                clean_amount = amount_raw.replace("$", "").replace(",", "")
                amount = float(clean_amount)
                if amount < 0:
                    errors.append("Amount cannot be negative.")
            except ValueError:
                errors.append("Please enter a valid numeric value for Amount.")

        valid_statuses = ["Pending", "Applied", "Approved", "Rejected"]
        if status not in valid_statuses:
            status = "Pending"

        if errors:
            for error in errors:
                flash(error, "danger")
            form_data = {
                "id": id,
                "scholarship_name": name,
                "provider": provider,
                "description": description,
                "eligibility": eligibility,
                "amount": amount_raw,
                "deadline": deadline,
                "application_link": application_link,
                "application_status": status,
            }
            return render_template("edit_scholarship.html", scholarship=form_data, active_page="scholarships")

        try:
            database.update_scholarship(
                scholarship_id=id,
                name=name,
                provider=provider,
                description=description,
                eligibility=eligibility,
                amount=amount,
                deadline=deadline,
                link=application_link,
                status=status,
            )
            flash(f"Scholarship '{name}' updated successfully!", "success")
            return redirect(url_for("scholarship_detail", id=id))
        except Exception as e:
            flash(f"Database error during update: {str(e)}", "danger")

    return render_template("edit_scholarship.html", scholarship=scholarship, active_page="scholarships")


@app.route("/scholarships/<int:id>/status", methods=["POST"])
def quick_update_status(id):
    """Quickly update the application status of a scholarship without opening edit form."""
    new_status = request.form.get("application_status", "").strip()
    valid_statuses = ["Pending", "Applied", "Approved", "Rejected"]

    if new_status in valid_statuses:
        success = database.update_scholarship_status(id, new_status)
        if success:
            flash(f"Application status updated to '{new_status}'.", "info")
        else:
            flash("Failed to update status. Scholarship not found.", "danger")
    else:
        flash("Invalid status selected.", "warning")

    # Redirect back to the referrer page if available, else to detail page
    return redirect(request.referrer or url_for("scholarship_detail", id=id))


@app.route("/scholarships/<int:id>/delete", methods=["POST"])
def delete_scholarship(id):
    """Delete a scholarship with a safety confirmation message."""
    try:
        deleted_name = database.delete_scholarship(id)
        if deleted_name:
            flash(f"Scholarship '{deleted_name}' has been deleted.", "success")
        else:
            flash("Scholarship not found or already deleted.", "warning")
    except Exception as e:
        flash(f"Error deleting scholarship: {str(e)}", "danger")

    return redirect(url_for("scholarships_list"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", error=str(e)), 500


if __name__ == "__main__":
    # Ensure database tables exist and sample data is initialized
    database.init_db()
    print("=" * 60)
    print(" Scholar Track - Scholarship Management System")
    print(" Server running locally at: http://127.0.0.1:5000/")
    print(" Press CTRL+C to stop the development server.")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
