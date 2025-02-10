import { SelectSection } from "./components/select_section.js";

const AssessmentTable = {
    props: ["assessments"],
    template: `
        <table class="table table-bordered">
            <thead class="thead-dark">
                <tr>
                    <th>Type</th>
                    <th>Assessment Count</th>
                    <th>Allocated Weight (%)</th>
                    <th>Completion</th>
                    <th>Average</th>
                    <th>Highest</th>
                    <th>Lowest</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="assessment in assessments" :key="assessment.type">
                    <td>{{ assessment.type }}</td>
                    <td>{{ assessment.assessment_count || 0 }}</td>
                    <td>{{ assessment.allocated_weight || 0 }}%</td>
                    <td>
                        <div class="progress">
                            <div class="progress-bar" role="progressbar"
                                 :style="{ width: (assessment.completion_percentage/assessment.allocated_weight)*100 + '%' }"
                                 :aria-valuenow="(assessment.completion_percentage/assessment.allocated_weight)*100"
                                 aria-valuemin="0"
                                 :aria-valuemax="assessment.allocated_weight">
                                {{ (assessment.completion_percentage/assessment.allocated_weight)*100 || 0 }}%
                            </div>
                        </div>
                    </td>
                    <td>{{ assessment.average || "N/A" }}</td>
                    <td>{{ assessment.highest || "N/A" }}</td>
                    <td>{{ assessment.lowest || "N/A" }}</td>
                </tr>
            </tbody>
        </table>
    `
};

const StudentTable = {
    props: ["students", "assessments"],
    template: `
        <table class="table table-bordered">
            <thead class="thead-dark">
                <tr>
                    <th rowspan="2">Students</th>
                    <th v-for="assessment in assessments" :colspan="2">{{ assessment.type }}</th>
                    <th rowspan="2">Course Total</th>
                </tr>
                <tr>
                    <th v-for="assessment in assessments">Total</th>
                    <th v-for="assessment in assessments">Weightage</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="student in students" :key="student.student_name">
                    <td>{{ student.student_name || "N/A" }}</td>
                    <td v-for="assessment in assessments">
                        {{ student.assessment_type_score[assessment.type]?.obtained_score || 0 }}
                    </td>
                    <td v-for="assessment in assessments">
                        {{ student.assessment_type_score[assessment.type]?.adjusted_score || 0 }}
                    </td>
                    <td>{{ student.adjusted_course_score ? student.adjusted_course_score.toFixed(2) : "0.00" }}</td>
                </tr>
            </tbody>
        </table>
    `
};

const app = Vue.createApp({
    components: {
        SelectSection,
        AssessmentTable,
        StudentTable
    },
    data() {
        return {
            sections: [],
            selectedSection: "",
            showStudents: false,
            assessments: [],
            students: []
        };
    },
    watch: {
        selectedSection(newVal) {
            if (newVal) {
                this.fetchSectionData(newVal);
            } else {
                this.assessments = [];
                this.students = [];
            }
        },
        showStudents() {
            if (this.selectedSection) {
                this.fetchSectionData(this.selectedSection);
            }
        }
    },
    methods: {
        fetchSections() {
            fetch('/api/sections/')
                .then(res => res.json())
                .then(data => this.sections = data)
                .catch(err => console.error("Error fetching sections:", err));
        },
        fetchSectionData(sectionId) {
            fetch(`/api/faculty/section/${sectionId}/final_result/?show_students=${this.showStudents}`)
                .then(res => res.json())
                .then(data => {
                    this.assessments = data.assessment_types || [];
                    this.students = data.students || [];
                })
                .catch(err => console.error("Error fetching section data:", err));
        }
    },
    mounted() {
        this.fetchSections();
    }
});

app.mount("#app");
