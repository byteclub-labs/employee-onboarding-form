/* Employee Onboarding — validate the form, submit it, render the list.
   All user-supplied text reaches the DOM via textContent only. */

(function () {
  "use strict";

  var DEPARTMENTS = [
    "Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Other",
  ];
  var EMPLOYMENT_TYPES = ["Full-time", "Part-time", "Contract"];
  var EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  var DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

  var form = document.getElementById("onboarding-form");
  var formError = document.getElementById("form-error");
  var formNote = document.getElementById("form-note");
  var employeesList = document.getElementById("employees-list");
  var employeesCount = document.getElementById("employees-count");

  function show(el, msg) {
    el.textContent = msg;
    el.hidden = false;
  }

  function hide(el) {
    el.hidden = true;
    el.textContent = "";
  }

  function api(path, options) {
    return fetch(path, options).then(function (res) {
      return res.json().then(function (data) {
        if (!res.ok) {
          throw new Error(data.error || "Something went wrong.");
        }
        return data;
      });
    });
  }

  function postJSON(path, payload) {
    return api(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }

  function isRealDate(iso) {
    if (!DATE_RE.test(iso)) {
      return false;
    }
    var d = new Date(iso + "T00:00:00");
    return !isNaN(d.getTime()) &&
      d.getFullYear() === Number(iso.slice(0, 4)) &&
      d.getMonth() === Number(iso.slice(5, 7)) - 1 &&
      d.getDate() === Number(iso.slice(8, 10));
  }

  function validate(payload) {
    if (!payload.full_name) {
      return "Full name is required.";
    }
    if (!payload.email || !EMAIL_RE.test(payload.email)) {
      return "A valid email address is required.";
    }
    if (!payload.phone) {
      return "Phone number is required.";
    }
    if (!payload.job_title) {
      return "Job title is required.";
    }
    if (DEPARTMENTS.indexOf(payload.department) === -1) {
      return "Please choose a department from the list.";
    }
    if (!isRealDate(payload.start_date)) {
      return "A valid start date is required.";
    }
    if (EMPLOYMENT_TYPES.indexOf(payload.employment_type) === -1) {
      return "Please choose an employment type from the list.";
    }
    return "";
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    hide(formError);
    hide(formNote);
    var payload = {
      full_name: document.getElementById("emp-name").value.trim(),
      email: document.getElementById("emp-email").value.trim(),
      phone: document.getElementById("emp-phone").value.trim(),
      job_title: document.getElementById("emp-job-title").value.trim(),
      department: document.getElementById("emp-department").value,
      start_date: document.getElementById("emp-start-date").value,
      employment_type: document.getElementById("emp-employment-type").value,
      address: document.getElementById("emp-address").value.trim(),
      emergency_contact_name: document.getElementById("emp-ec-name").value.trim(),
      emergency_contact_phone: document.getElementById("emp-ec-phone").value.trim(),
      notes: document.getElementById("emp-notes").value.trim(),
    };
    var problem = validate(payload);
    if (problem) {
      show(formError, problem);
      return;
    }
    var button = form.querySelector("button");
    button.disabled = true;
    postJSON("/api/employees", payload)
      .then(function () {
        form.reset();
        show(formNote, "Employee onboarded.");
        loadEmployees();
      })
      .catch(function (err) {
        show(formError, err.message);
      })
      .finally(function () {
        button.disabled = false;
      });
  });

  function formatDate(iso) {
    var d = new Date(iso + "T00:00:00");
    if (isNaN(d.getTime())) {
      return iso;
    }
    return d.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  function renderEmployees(employees) {
    while (employeesList.firstChild) {
      employeesList.removeChild(employeesList.firstChild);
    }
    if (employees.length === 0) {
      var empty = document.createElement("p");
      empty.className = "list-empty";
      empty.textContent = "No employees onboarded yet — submit the form above to add the first.";
      employeesList.appendChild(empty);
      return;
    }
    employees.forEach(function (emp) {
      var card = document.createElement("article");
      card.className = "employee-card";

      var meta = document.createElement("p");
      meta.className = "employee-meta";

      var name = document.createElement("span");
      name.className = "employee-name";
      name.textContent = emp.full_name;
      meta.appendChild(name);

      var role = [emp.job_title, emp.department]
        .filter(function (s) {
          return s;
        })
        .join(" · ");
      if (role) {
        meta.appendChild(document.createTextNode(" — " + role));
      }

      var date = document.createElement("span");
      date.className = "employee-date";
      date.textContent = "Starts " + formatDate(emp.start_date);
      meta.appendChild(date);

      card.appendChild(meta);
      employeesList.appendChild(card);
    });
  }

  function loadEmployees() {
    return api("/api/employees")
      .then(function (data) {
        if (data.count === 0) {
          employeesCount.textContent = "No employees onboarded yet.";
        } else if (data.count === 1) {
          employeesCount.textContent = "1 employee onboarded";
        } else {
          employeesCount.textContent = data.count + " employees onboarded";
        }
        renderEmployees(data.employees);
      })
      .catch(function () {
        employeesCount.textContent = "Could not load onboarded employees right now.";
      });
  }

  loadEmployees();
})();
