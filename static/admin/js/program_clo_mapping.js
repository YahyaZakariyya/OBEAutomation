document.addEventListener('DOMContentLoaded', function() {
    const programField = $('#id_program');  // Using jQuery selector for Select2 compatibility
    const courseField = $('#id_course');
    const cloField = $('#id_clo');
    const ploField = $('#id_plo');
    const weightageField = $('#id_weightage');

    function fetchRelatedData(url, targetField) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                targetField.empty();  // Clear existing options
                data.forEach(item => {
                    const option = new Option(item.name, item.id, false, false);
                    targetField.append(option);
                });
                targetField.trigger('change');  // Trigger change to update Select2
            })
            .catch(error => console.error("Error fetching data:", error));
    }

    // Event listener to handle weightage distribution on PLO selection change
    ploField.on('change', function() {
        const selectedPLOs = ploField.val();  // Array of selected PLOs
        const weightage = parseFloat(weightageField.val()) || 0;

        if (selectedPLOs.length > 0 && weightage > 0) {
            const distributedWeightage = (weightage / selectedPLOs.length).toFixed(2);
            console.log("Distributed Weightage per PLO:", distributedWeightage);

            // Optional: Display distributed weightage per PLO (update UI accordingly)
            // You could append or display the distributed weightage next to each selected PLO
        }
    });

    // Event listener for Program field
    programField.on('change', function() {
        const programId = programField.val();
        if (programId) {
            const url = `/obesystem/programclomapping/get_plos/?program_id=${programId}`;
            fetchRelatedData(url, ploField);
        } else {
            ploField.empty();  // Clear PLO options if no program is selected
            ploField.trigger('change');  // Trigger change to update Select2
        }
    });

    // Event listener for Course field
    courseField.on('change', function() {
        const courseId = courseField.val();
        if (courseId) {
            const url = `/obesystem/programclomapping/get_clos/?course_id=${courseId}`;
            fetchRelatedData(url, cloField);
        } else {
            cloField.empty();  // Clear CLO options if no course is selected
            cloField.trigger('change');  // Trigger change to update Select2
        }
    });
});
