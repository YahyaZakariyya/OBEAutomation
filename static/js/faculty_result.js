document.addEventListener("DOMContentLoaded", () => {
    const sectionDropdown = document.getElementById("section");
    const showStudentsCheckbox = document.getElementById("show_students");
    const studentsTable = document.getElementById("students-table");
    const assessmentTable = document.getElementById("assessment-table");

    // Fetch sections from the API and populate the dropdown
    fetch('/api/sections/')
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch sections.");
            }
            return response.json();
        })
        .then(data => {
            // Validate the structure of the response
            if (!Array.isArray(data)) {
                console.error("Unexpected sections data format", data);
                return;
            }

            // Populate the dropdown with the fetched sections
            data.forEach(section => {
                const option = document.createElement("option");
                option.value = section.id;
                option.text = section.name || `Section ${section.id}`;
                sectionDropdown.add(option);
            });
        })
        .catch(error => {
            console.error("Error fetching sections:", error);
        });

    // Event listener for section selection
    sectionDropdown.addEventListener("change", () => {
        const sectionId = sectionDropdown.value;

        if (sectionId) {
            // Fetch assessment details and student data for the selected section
            fetch(`/api/faculty/section/${sectionId}/final_result/?show_students=true`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Failed to fetch section data.");
                    }
                    return response.json();
                })
                .then(data => {
                    // Clear the tables before populating new data
                    assessmentTable.innerHTML = "";
                    studentsTable.innerHTML = "";

                    // Handle assessment types
                    if (data.assessment_types && Array.isArray(data.assessment_types)) {
                        data.assessment_types.forEach(assessment => {
                            const row = document.createElement("tr");
                            row.innerHTML = `
                                <td>${assessment.type}</td>
                                <td>${assessment.assessment_count || 0}</td>
                                <td>${assessment.allocated_weight || 0}%</td>
                                <td>
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" style="width: ${(assessment.completion_percentage/assessment.allocated_weight)*100 || 0}%" aria-valuenow="${(assessment.completion_percentage/assessment.allocated_weight)*100 || 0}" aria-valuemin="0" aria-valuemax="${assessment.allocated_weight}">${(assessment.completion_percentage/assessment.allocated_weight)*100 || 0}%</div>
                                    </div>
                                </td>
                                <td>${assessment.average || "N/A"}</td>
                                <td>${assessment.highest || "N/A"}</td>
                                <td>${assessment.lowest || "N/A"}</td>
                            `;
                            assessmentTable.appendChild(row);
                        });
                    } else {
                        console.warn("No assessment types found for the section.");
                    }

                    // Handle students (only if "Show Students" is checked)
                    if (showStudentsCheckbox.checked && data.students && Array.isArray(data.students)) {
                        // Clear the table header and body first
                        const studentTableHeader = document.createElement("thead");
                        studentTableHeader.classList.add("thead-dark");
                        const studentTableBody = document.createElement("tbody");
                        studentsTable.innerHTML = ""; // Clear previous data

                        // Create the top header for the table
                        const topHeaderRow = document.createElement("tr");
                        topHeaderRow.innerHTML = `
                            <th rowspan="2">Students</th>
                        `;
                        if (data.assessment_types) {
                            data.assessment_types.forEach((type) => {
                                topHeaderRow.innerHTML += `
                                    <th colspan="2">${type.type}</th>
                                `;
                            });
                        }
                        topHeaderRow.innerHTML += `<th rowspan="2">Course Total</th>`;
                        studentTableHeader.appendChild(topHeaderRow);

                        // Create the sub-header row
                        const subHeaderRow = document.createElement("tr");
                        if (data.assessment_types) {
                            data.assessment_types.forEach(() => {
                                subHeaderRow.innerHTML += `
                                    <th>Total</th>
                                    <th>Weightage</th>
                                `;
                            });
                        }
                        studentTableHeader.appendChild(subHeaderRow);
                        studentsTable.appendChild(studentTableHeader);

                        // Populate the rows with student data
                        data.students.forEach(student => {
                            const row = document.createElement("tr");
                            row.innerHTML = `
                                <td>${student.student_name || "N/A"}</td>
                            `;
                            if (student.assessment_type_score) {
                                Object.keys(student.assessment_type_score).forEach((type) => {
                                    const typeScore = student.assessment_type_score[type];
                                    row.innerHTML += `
                                        <td>${typeScore.obtained_score || 0}</td>
                                        <td>${typeScore.adjusted_score || 0}</td>
                                    `;
                                });
                            }
                            row.innerHTML += `
                                <td>${student.adjusted_course_score ? student.adjusted_course_score.toFixed(2) : "0.00"}</td>
                            `;
                            studentTableBody.appendChild(row);
                        });
                        studentsTable.appendChild(studentTableBody);
                    } else if (showStudentsCheckbox.checked) {
                        console.warn("No students found for the section.");
                    }

                })
                .catch(error => {
                    console.error("Error fetching section data:", error);
                });
        } else {
            // Clear tables if no section is selected
            assessmentTable.innerHTML = "";
            studentsTable.innerHTML = "";
        }
    });

    // Event listener for showing or hiding students
    showStudentsCheckbox.addEventListener("change", () => {
        const sectionId = sectionDropdown.value;

        if (sectionId && showStudentsCheckbox.checked) {
            // Trigger the section dropdown change event to reload data
            sectionDropdown.dispatchEvent(new Event("change"));
        } else {
            // Clear the students table if unchecked
            studentsTable.innerHTML = "";
        }
    });
});
