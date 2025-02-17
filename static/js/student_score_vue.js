const app = Vue.createApp({
    data() {
        return {
            student: {},
            table: {
                questions: [],
                clos: [],
                total_marks: [],
                obtained_marks: []
            },
            errorMessage: "",
            assessmentId: null,
            studentId: null
        };
    },
    created() {
        // ✅ Extract assessment ID and student ID from URL
        const params = new URLSearchParams(window.location.search);
        this.assessmentId = params.get('assessment_id');
        this.studentId = params.get('student_id');

        if (this.assessmentId && this.studentId) {
            this.fetchStudentScore();
        } else {
            this.errorMessage = "Missing required parameters.";
        }
    },
    methods: {
        async fetchStudentScore() {
            try {
                const response = await fetch(`/api/student-score/?student_id=${this.studentId}&assessment_id=${this.assessmentId}`);
                if (!response.ok) throw new Error("Failed to fetch student scores.");

                const data = await response.json();
                this.student = data.student;
                this.table = data.table;
            } catch (error) {
                this.errorMessage = error.message;
            }
        }
    },
    template: `
    <div class="container mt-4">
        <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

        <div v-if="Object.keys(student).length" class="card mb-3">
            <div class="card-body">
                <h4 class="card-title">{{ student.first_name }} {{ student.last_name }}</h4>
                <p class="card-text"><strong>Username:</strong> {{ student.username }}</p>
            </div>
        </div>

        <!-- Responsive Table Wrapper -->
        <div class="table-responsive">
            <table v-if="table.questions.length" class="table table-bordered text-center">
                <thead>
                    <tr>
                        <th>Questions</th>
                        <th v-for="question in table.questions">{{ question }}</th>
                    </tr>
                    <tr>
                        <th>CLOs</th>
                        <th v-for="clo_list in table.clos">
                            <span v-for="clo in clo_list" class="badge bg-info text-white">{{ clo }}</span>
                        </th>
                    </tr>
                    <tr>
                        <th>Total Marks</th>
                        <th v-for="marks in table.total_marks">{{ marks }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="table-success">
                        <th>Obtained Marks</th>
                        <td v-for="marks in table.obtained_marks">{{ marks }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
`

});

// Register Vue Component
app.component('student-score', {
    template: app.template,
    data: app.data,
    methods: app.methods,
    created: app.created
});

// Mount Vue App
app.mount("#app");
