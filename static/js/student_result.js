document.addEventListener("DOMContentLoaded", function () {
    const apiUrl = "/api/results/";
    let assessmentData = null;

    // DOM Elements
    const sectionFilter = document.getElementById("section-filter");
    const overviewBlock = document.getElementById("overview");
    const assessmentFilterBlock = document.getElementById("assessment-filter-block");
    const assessmentFilter = document.getElementById("assessment-filter");
    const resultsBlock = document.getElementById("results-block");
    const majorTableBlock = document.getElementById("major-table-block");

    const totalWeight = document.getElementById("total-weight");
    const courseCompletion = document.getElementById("course-completion");
    const overallScore = document.getElementById("overall-score");

    const assessmentTable = document.getElementById("assessment-table");
    const majorTable = document.getElementById("major-table");
    const downloadCSVButton = document.getElementById("download-csv");

    const overviewChartCanvas = document.getElementById("overviewChart");
    const assessmentChartCanvas = document.getElementById("assessmentChart");

    let overviewChart, assessmentChart;

    // Section Selection Logic
    sectionFilter.addEventListener("change", function () {
        const sectionId = this.value;
        resetUI();

        if (sectionId) {
            fetch(`${apiUrl}?section_id=${sectionId}`)
                .then((response) => response.json())
                .then((data) => {
                    assessmentData = data;
                    populateOverview(data);
                    populateAssessmentFilter(data.assessment_types);
                    populateMajorTable(data);
                    majorTableBlock.style.display = "block";
                })
                .catch((error) => console.error("Error fetching data:", error));
        }
    });

    // Populate Overview Section
    function populateOverview(data) {
        overviewBlock.style.display = "block";
        totalWeight.textContent = data.total_weight;
        courseCompletion.textContent = data.course_completion.toFixed(2);
        overallScore.textContent = data.student_current_overall.toFixed(2);

        renderOverviewChart(data.assessment_types);
    }

    function renderOverviewChart(types) {
        destroyChart(overviewChart);
        overviewChart = new Chart(overviewChartCanvas.getContext("2d"), {
            type: "pie",
            data: {
                labels: types.map((t) => t.type),
                datasets: [
                    {
                        data: types.map((t) => t.allocated_weight),
                        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
                    },
                ],
            },
        });
    }

    // Populate Assessment Filter
    function populateAssessmentFilter(types) {
        assessmentFilterBlock.style.display = "block";
        assessmentFilter.innerHTML = `<option value="">-- Select Assessment Type --</option>`;
        types.forEach((type, index) => {
            const option = document.createElement("option");
            option.value = index;
            option.textContent = type.type;
            assessmentFilter.appendChild(option);
        });
    }

    // Handle Assessment Filter Change
    assessmentFilter.addEventListener("change", function () {
        const selectedIndex = this.value;
        if (selectedIndex !== "") {
            const selectedType = assessmentData.assessment_types[selectedIndex];
            populateAssessmentDetails(selectedType);
            renderAssessmentChart(selectedType.assessments);
            resultsBlock.style.display = "flex";
        } else {
            resetResults();
        }
    });

    // Populate Assessment Details Table
    function populateAssessmentDetails(type) {
        assessmentTable.innerHTML = "";
        type.assessments.forEach((a) => {
            const row = `
                <tr>
                    <td rowspan="1">${type.type}</td>
                    <td>${a.title}</td>
                    <td>${a.student_obtained_marks}</td>
                    <td>${a.total_marks}</td>
                    <td>${a.adjusted_marks.toFixed(2)}</td>
                    <td>${a.assessment_weight}</td>
                    <td>${type.completed_weightage || 0}</td>
                    <td>${a.adjusted_obtained_marks?.toFixed(2) || 0}</td>
                    <td>${type.allocated_weight}</td>
                </tr>`;
            assessmentTable.insertAdjacentHTML("beforeend", row);
        });
    }

    // Render Assessment Chart
    function renderAssessmentChart(assessments) {
        destroyChart(assessmentChart);
        assessmentChart = new Chart(assessmentChartCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: assessments.map((a) => a.title),
                datasets: [
                    {
                        label: "Obtained Marks",
                        data: assessments.map((a) => a.student_obtained_marks),
                        backgroundColor: "#36A2EB",
                    },
                    {
                        label: "Adjusted Marks",
                        data: assessments.map((a) => a.adjusted_marks),
                        backgroundColor: "#FF6384",
                    },
                ],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    }

    // Populate Major Table
    function populateMajorTable(data) {
        majorTable.innerHTML = ""; // Clear table
    
        // Iterate through assessment types
        data.assessment_types.forEach((type) => {
    
            // Check if assessments exist
            if (type.assessments && type.assessments.length > 0) {
                // Process types with assessments
                type.assessments.forEach((a, idx) => {
                    // Create table rows
                    const row = `
                        <tr>
                            ${
                                idx === 0
                                    ? `<td rowspan="${type.assessments.length}" class="align-middle">${type.type}</td>`
                                    : ""
                            }
                            <td>${a.title}</td>
                            <td>${a.student_obtained_marks}</td>
                            <td>${a.total_marks}</td>
                            <td>${a.adjusted_marks.toFixed(2)}</td>
                            <td>${a.assessment_weight}</td>
                            ${ idx === 0 ? `<td rowspan="${type.assessments.length}" class="align-middle">${type.completion_percentage.toFixed(2)}</td>`: ""}
                            ${ idx === 0 ? `<td rowspan="${type.assessments.length}" class="align-middle">${type.adjusted_marks.toFixed(2)}</td>`: ""}
                            ${ idx === 0 ? `<td rowspan="${type.assessments.length}" class="align-middle">${type.allocated_weight}</td>`: ""}
                        </tr>`;
                    majorTable.insertAdjacentHTML("beforeend", row);
                });
            } else {
                // Placeholder row for types with no assessments
                const row = `
                    <tr>
                        <td class="align-middle">${type.type}</td>
                        <td>-</td>
                        <td>0</td>
                        <td>0</td>
                        <td>0.00</td>
                        <td>0</td>
                        <td>${type.completion_percentage.toFixed(2)}</td>
                        <td>${type.adjusted_marks.toFixed(2)}</td>
                        <td>${type.allocated_weight}</td>
                    </tr>`;
                majorTable.insertAdjacentHTML("beforeend", row);
            }    
        });
    
        // Append Total Row
        const totalRow = `
            <tr class="table-dark fw-bold">
                <td colspan="7">Total</td>
                <td class="bg-danger">${data.student_current_overall.toFixed(2)}</td>
                <td>${data.total_weight}</td>
            </tr>`;
        majorTable.insertAdjacentHTML("beforeend", totalRow);
    }
    
    

    // Download Table as CSV
    downloadCSVButton.addEventListener("click", function () {
        let csvContent = "data:text/csv;charset=utf-8,";
        const rows = majorTable.closest("table").querySelectorAll("tr");

        rows.forEach((row) => {
            const cols = row.querySelectorAll("th, td");
            const rowData = Array.from(cols).map((col) => col.innerText).join(",");
            csvContent += rowData + "\n";
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "student_results.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // Utility Functions
    function destroyChart(chart) {
        if (chart) chart.destroy();
    }

    function resetUI() {
        overviewBlock.style.display = "none";
        assessmentFilterBlock.style.display = "none";
        resultsBlock.style.display = "none";
        majorTableBlock.style.display = "none";
        destroyChart(overviewChart);
        destroyChart(assessmentChart);
    }

    function resetResults() {
        assessmentTable.innerHTML = "";
        destroyChart(assessmentChart);
    }
});
