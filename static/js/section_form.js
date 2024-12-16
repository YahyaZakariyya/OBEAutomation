document.addEventListener('DOMContentLoaded', function () {
    const programField = $('#id_program'); // Program dropdown
    const courseField = $('#id_course');   // Course dropdown

    // Clear fields initially if no program is selected
    if (!programField.val()) {
        courseField.empty().trigger('change');
    }

    // When the program changes
    programField.on('change', function () {
        const programId = programField.val();

        // Clear Course field
        courseField.empty().trigger('change');
        
        if (programId) {
            // Fetch Courses for the selected program
            fetch(`/api/courses/${programId}/`)
                .then(response => response.json())
                .then(courses => {
                    courses.forEach(course => {
                        const option = new Option(course.name, course.id, false, false);
                        courseField.append(option);
                    });
                    courseField.trigger('change');
                })
                .catch(error => console.error('Error fetching courses:', error));
        }
    });
});
