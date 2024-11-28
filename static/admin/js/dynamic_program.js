document.addEventListener('DOMContentLoaded', function () {
    const programField = $('#id_program');
    const courseField = $('#id_course');

    // Clear course field initially if no program is selected
    if (!programField.val()) {
        courseField.empty().trigger('change'); // Clear Select2 options
    }

    // When the program is changed
    programField.on('change', function () {
        const programId = programField.val(); // Get the selected program ID

        // Clear the course field
        courseField.empty(); // Clear existing options

        if (programId) {
            // Fetch courses for the selected program
            fetch(`/obesystem/section/get-courses/?program_id=${programId}`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then((courses) => {
                    // Populate the course field with new options
                    courses.forEach((course) => {
                        const newOption = new Option(course.name, course.id, false, false);
                        courseField.append(newOption);
                    });

                    // Refresh the Select2 dropdown
                    courseField.trigger('change');
                })
                .catch((error) => {
                    console.error('Error fetching courses:', error);
                });
        } else {
            // If no program is selected, ensure the dropdown is cleared
            courseField.empty().trigger('change');
        }
    });
});