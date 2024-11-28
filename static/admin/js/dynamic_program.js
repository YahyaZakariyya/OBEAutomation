document.addEventListener('DOMContentLoaded', function() {
    const programField = $('#id_program');  // jQuery selector for Program field
    const courseField = $('#id_course');    // jQuery selector for Course field

    function fetchRelatedCourses(url, targetField) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                targetField.empty();  // Clear existing options
                data.forEach(course => {
                    const option = new Option(course.name, course.id, false, false);
                    targetField.append(option);
                });
                targetField.trigger('change');  // Trigger change to update Select2 if in use
            })
            .catch(error => console.error("Error fetching courses:", error));
    }

    // Event listener for Program field
    programField.on('change', function() {
        const programId = programField.val();
        if (programId) {
            const url = `/obesystem/section/get-courses/?program_id=${programId}`;
            fetchRelatedCourses(url, courseField);
            courseField.show();  // Show the course field after populating it
        } else {
            courseField.empty();  // Clear options if no program is selected
            courseField.hide();   // Hide course field if no program is selected
        }
    });

    // Hide course dropdown initially
    courseField.hide();
});
