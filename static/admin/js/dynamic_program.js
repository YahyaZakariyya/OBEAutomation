document.addEventListener("DOMContentLoaded", function() {
    const courseField = document.getElementById("id_course");
    const programField = document.getElementById("id_program");

    courseField.addEventListener("change", function() {
        const courseId = courseField.value;
        if (courseId) {
            fetch(`/get-programs/?course_id=${courseId}`)
                .then(response => response.json())
                .then(data => {
                    // Clear the current options
                    programField.innerHTML = '';
                    // Add new options
                    data.programs.forEach(program => {
                        const option = document.createElement("option");
                        option.value = program.id;
                        option.text = program.name;
                        programField.appendChild(option);
                    });
                });
        } else {
            // Clear the program options if no course is selected
            programField.innerHTML = '';
        }
    });
});
