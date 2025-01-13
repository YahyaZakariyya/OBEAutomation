document.addEventListener("DOMContentLoaded", function () {
    const apiUrl = "/api/results/";
    let assessmentData = null;

    // DOM Elements
    const sectionFilter = document.getElementById("section-filter");
    const overviewBlock = document.getElementById("overview");
    const majorTableBlock = document.getElementById("major-table-block");

    const totalWeight = document.getElementById("total-weight");
    const courseCompletion = document.getElementById("course-completion");
    const overallScore = document.getElementById("overall-score");

    const majorTable = document.getElementById("major-table");
    const downloadCSVButton = document.getElementById("download-csv");

    const overviewChartCanvas = document.getElementById("overviewChart");

    let overviewChart;

    // Section Selection Logic
    sectionFilter.addEventListener("change", function () {
        const sectionId = this.value;
        resetUI();

        if (sectionId) {
            fetch(`${apiUrl}?section_id=${sectionId}`)
                .then((response) => response.json())
                .then((data) => {
                    populateOverview(data);
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
            type: "doughnut",
            data: {
                labels: types.map((t) => t.type),
                datasets: [
                    {
                        data: types.map((t) => t.allocated_weight),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(255, 159, 64, 0.2)',
                            'rgba(255, 205, 86, 0.2)',
                            'rgba(75, 192, 192, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(153, 102, 255, 0.2)',
                            'rgba(201, 203, 207, 0.2)'],
                        borderColor: [
                            'rgb(255, 99, 132)',
                            'rgb(255, 159, 64)',
                            'rgb(255, 205, 86)',
                            'rgb(75, 192, 192)',
                            'rgb(54, 162, 235)',
                            'rgb(153, 102, 255)',
                            'rgb(201, 203, 207)'
                            ],
                        borderWidth: 1,
                    },
                ],
            },
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
        majorTableBlock.style.display = "none";
        destroyChart(overviewChart);
    }
});
