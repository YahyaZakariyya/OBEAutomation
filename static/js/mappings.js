document.addEventListener('DOMContentLoaded', function () {
    const programField = $('#id_program'); // Program dropdown
    const courseField = $('#id_course');   // Course dropdown
    const ploField = $('#id_plo');         // PLO dropdown
    const cloField = $('#id_clo');         // CLO dropdown

    // Clear fields initially if no program is selected
    if (!programField.val()) {
        courseField.empty().trigger('change');
        ploField.empty().trigger('change');
        cloField.empty().trigger('change');
    }

    // When the program changes
    programField.on('change', function () {
        const programId = programField.val();

        // Clear Course and PLO fields
        courseField.empty().trigger('change');
        ploField.empty().trigger('change');
        cloField.empty().trigger('change');

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

            // Fetch PLOs for the selected program
            fetch(`/api/plos/${programId}/`)
                .then(response => response.json())
                .then(plos => {
                    plos.forEach(plo => {
                        const option = new Option(`(PLO ${plo.PLO}) - ${plo.heading}`, plo.id, false, false);
                        ploField.append(option);
                    });
                    ploField.trigger('change');
                })
                .catch(error => console.error('Error fetching PLOs:', error));
        }
    });

    // When the course changes
    courseField.on('change', function () {
        const courseId = courseField.val();

        // Clear CLO field
        cloField.empty().trigger('change');

        if (courseId) {
            // Fetch CLOs for the selected course
            fetch(`/api/clos/${courseId}/`)
                .then(response => response.json())
                .then(clos => {
                    clos.forEach(clo => {
                        const option = new Option(`(CLO ${clo.CLO}) - ${clo.heading}`, clo.id, false, false);
                        cloField.append(option);
                    });
                    cloField.trigger('change');
                })
                .catch(error => console.error('Error fetching CLOs:', error));
        }
    });
});
