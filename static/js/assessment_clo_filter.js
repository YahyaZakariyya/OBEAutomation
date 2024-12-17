document.addEventListener('DOMContentLoaded', function () {
    const cloFieldsSelector = 'select[id$="-clo"]'; // Match CLO fields in the inline form
    const sectionField = document.querySelector('#id_section'); // Section field
    
    function fetchAndPopulateCLOs(courseId) {
        fetch(`/api/clos/${parseInt(courseId)}/`)
            .then(response => response.json())
            .then(data => {
                const cloFields = document.querySelectorAll(cloFieldsSelector);

                cloFields.forEach(cloField => {
                    const selectedOptions = Array.from(cloField.options)
                                                .filter(option => option.selected)
                                                .map(option => option.value);

                    cloField.innerHTML = ''; // Clear existing options

                    data.forEach(clo => {
                        const option = new Option(`(CLO ${clo.CLO}) - ${clo.heading}`, clo.id, false, false);
                        if (selectedOptions.includes(String(clo.id))) {
                            option.selected = true; // Re-select already assigned CLOs
                        }
                        cloField.appendChild(option);
                    });
                });
            })
            .catch(error => console.error("Error fetching CLOs:", error));
    }

    function initCLOPopulation() {
        const sectionId = sectionField.value;
        if (sectionId) {
            fetch(`/api/get-course-id/?section_id=${sectionId}`)
                .then(response => response.json())
                .then(data => {
                    const courseId = data.course_id;
                    if (courseId) {
                        fetchAndPopulateCLOs(courseId);
                    }
                })
                .catch(error => console.error("Error fetching Course ID:", error));
        }
    }

    // Trigger on page load
    initCLOPopulation();
});
