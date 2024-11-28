// document.addEventListener("DOMContentLoaded", function () {
//     function updateQuestionNumbers() {
//         const rows = document.querySelectorAll(".dynamic-questions");
//         rows.forEach(function (row, index) {
//             const numberField = row.querySelector("input[name$='-number']");
//             const numberDisplay = row.querySelector(".field-number");

//             if (numberField && numberDisplay) {
//                 // Ensure only the number is stored in the database
//                 const questionNumber = index + 1;
//                 numberField.value = questionNumber;

//                 // Add "Q" prefix in the UI without modifying the input field
//                 numberDisplay.textContent = `Q${questionNumber}`;
//             }
//         });
//     }

//     function insertQuestionRow(row) {
//         // Clone the empty form template
//         const emptyForm = document.querySelector("tr.empty-form");
//         const newRow = emptyForm.cloneNode(true);
//         newRow.classList.remove("empty-form");
//         newRow.style.display = "";

//         // Insert the new row after the current row
//         row.parentNode.insertBefore(newRow, row.nextSibling);

//         // Reinitialize the formset to update management form counts
//         const totalForms = document.querySelector("#id_questions-TOTAL_FORMS");
//         totalForms.value = parseInt(totalForms.value) + 1;

//         // Update question numbers
//         updateQuestionNumbers();
//         addInsertButtons();
//     }

//     function setupRowListeners() {
//         const addRowButton = document.querySelector("tr.add-row a");
//         if (addRowButton && !addRowButton.dataset.listener) {
//             addRowButton.dataset.listener = "true"; // Prevent duplicate listeners
//             addRowButton.addEventListener("click", () => {
//                 setTimeout(() => {
//                     updateQuestionNumbers();
//                     addInsertButtons();
//                 }, 100); // Wait for row to be added
//             });
//         }

//         const deleteCheckboxes = document.querySelectorAll("td.delete input[type='checkbox']");
//         deleteCheckboxes.forEach((checkbox) => {
//             if (!checkbox.dataset.listener) {
//                 checkbox.dataset.listener = "true"; // Prevent duplicate listeners
//                 checkbox.addEventListener("change", () => {
//                     setTimeout(() => {
//                         updateQuestionNumbers();
//                         addInsertButtons();
//                     }, 100); // Wait for row to be removed
//                 });
//             }
//         });
//     }

//     // Monitor dynamic row additions
//     const observer = new MutationObserver(() => {
//         updateQuestionNumbers();
//         addInsertButtons();
//         setupRowListeners();
//     });

//     const targetNode = document.querySelector("#questions-tab table tbody");
//     if (targetNode) {
//         observer.observe(targetNode, { childList: true });
//     }

//     // Initial setup
//     updateQuestionNumbers();
//     addInsertButtons();
//     setupRowListeners();
// });


document.addEventListener("DOMContentLoaded", function () {
    function fetchCLOs(assessmentId, cloSelect) {
        const url = `/admin/obesystem/questioninline/fetch-clos/${assessmentId}/`;

        fetch(url)
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    console.error(data.error);
                } else {
                    // Clear existing options
                    cloSelect.innerHTML = "";

                    // Add new options dynamically
                    data.forEach((clo) => {
                        const option = document.createElement("option");
                        option.value = clo.id;
                        option.textContent = clo.name;
                        cloSelect.appendChild(option);
                    });
                }
            })
            .catch((error) => console.error("Error fetching CLOs:", error));
    }

    // Hook into each row and listen for changes
    const rows = document.querySelectorAll(".dynamic-questions");
    rows.forEach(function (row) {
        const assessmentField = row.querySelector("input[name$='-assessment']");
        const cloSelect = row.querySelector("select[name$='-clo']");

        if (assessmentField && cloSelect) {
            assessmentField.addEventListener("change", function () {
                const assessmentId = assessmentField.value;
                if (assessmentId) {
                    fetchCLOs(assessmentId, cloSelect);
                }
            });
        }
    });

    // Trigger fetch on page load
    document.querySelectorAll(".dynamic-questions").forEach((row) => {
        const assessmentField = row.querySelector("input[name$='-assessment']");
        const cloSelect = row.querySelector("select[name$='-clo']");

        if (assessmentField && cloSelect && assessmentField.value) {
            fetchCLOs(assessmentField.value, cloSelect);
        }
    });
});
