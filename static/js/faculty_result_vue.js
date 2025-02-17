import { SelectSection } from "./components/select_section.js";

const AssessmentTable = {
    props: ["assessments"],
    template: `
        <div class="card shadow-sm p-4 mb-4">
            <h5 class="mb-3">Assessment Details</h5>
            <div class="table-responsive" style="white-space: nowrap">
                <table class="table table-bordered text-center">
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
                            <td>{{ assessment.type.charAt(0).toUpperCase() + assessment.type.slice(1) }}</td>
                            <td>{{ assessment.assessment_count || 0 }}</td>
                            <td>{{ assessment.allocated_weight || 0 }}%</td>
                            <td>
                                <div class="progress">
                                    <div class="progress-bar" role="progressbar"
                                        :class="(assessment.completion_percentage / assessment.allocated_weight) * 100 === 100 ? 'bg-success' : 'bg-danger'"
                                        :style="{ width: (assessment.completion_percentage / assessment.allocated_weight) * 100 + '%' }"
                                        :aria-valuenow="(assessment.completion_percentage / assessment.allocated_weight) * 100"
                                        aria-valuemin="0"
                                        :aria-valuemax="assessment.allocated_weight">
                                        {{ ((assessment.completion_percentage / assessment.allocated_weight) * 100 || 0).toFixed(2) }}%
                                    </div>
                                </div>
                            </td>
                            <td>{{ assessment.average || "N/A" }}</td>
                            <td>{{ assessment.highest || "N/A" }}</td>
                            <td>{{ assessment.lowest || "N/A" }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `
};

const StudentTable = {
    props: ["students", "assessments"],
    template: `
        <div class="card shadow-sm p-4 mb-4">
            <h5 class="mb-3">Students Result</h5>
            <div class="table-responsive" style="white-space: nowrap">
                <table class="table table-bordered text-center">
                    <thead class="thead-dark">
                        <tr>
                            <th rowspan="3">Students</th>
                            <th v-for="assessment in assessments" :colspan="2">{{ assessment.type.charAt(0).toUpperCase() + assessment.type.slice(1) }}</th>
                            <th rowspan="3">Course Total</th>
                            <th rowspan="3">Grade</th>
                        </tr>
                        <tr>
                            <template v-for="assessment in assessments">
                                <th>Total.M</th>
                                <th>Adjusted.M</th>
                            </template>
                        </tr>
                        <tr>
                            <template v-for="assessment in assessments">
                                <th>{{assessment.total_type_marks }}</th>
                                <th>{{ assessment.allocated_weight }}</th>
                            </template>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="student in students" :key="student.student_id">
                            <td>{{ student.student_name || "N/A" }}</td>
                            <template v-for="assessment in assessments">
                                <td>{{ student.assessment_type_score[assessment.type]?.obtained_score || 0 }}</td>
                                <td>{{ student.assessment_type_score[assessment.type]?.adjusted_score.toFixed(2) || "0.00" }}</td>
                            </template>
                            <td class="font-weight-bold">{{ student.adjusted_course_score ? student.adjusted_course_score.toFixed(2) : "0.00" }}</td>
                            <td :class="['font-weight-bold', gradeClass(calculateGrade(student.adjusted_course_score))]">
                                <strong>{{ calculateGrade(student.adjusted_course_score) }}</strong>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `,
    methods: {
        calculateGrade(score) {
            if (score >= 90) return "A+";
            if (score >= 80) return "A";
            if (score >= 70) return "B";
            if (score >= 60) return "C";
            if (score >= 50) return "D";
            return "Fail";
        },
        gradeClass(grade) {
            switch (grade) {
                case "A+":
                case "A":
                    return "text-success";
                case "B":
                    return "text-primary";
                case "C":
                    return "text-info";
                case "D":
                    return "text-warning";
                case "Fail":
                    return "text-danger";
                default:
                    return "";
            }
        }
    }
};

const GradeDistributionTable = {
    props: ["students"],
    template: `
        <table class="table table-bordered">
            <thead class="thead-dark">
                <tr>
                    <th>Fail</th>
                    <th>D</th>
                    <th>C</th>
                    <th>B</th>
                    <th>A</th>
                    <th>A+</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{ countGrades("Fail") }}</td>
                    <td>{{ countGrades("D") }}</td>
                    <td>{{ countGrades("C") }}</td>
                    <td>{{ countGrades("B") }}</td>
                    <td>{{ countGrades("A") }}</td>
                    <td>{{ countGrades("A+") }}</td>
                </tr>
            </tbody>
        </table>
    `,
    methods: {
        countGrades(grade) {
            return this.students.filter(student => this.calculateGrade(student.adjusted_course_score) === grade).length;
        },
        calculateGrade(score) {
            if (score >= 90) return "A+";
            if (score >= 80) return "A";
            if (score >= 70) return "B";
            if (score >= 60) return "C";
            if (score >= 50) return "D";
            return "Fail";
        }
    }
};

const app = Vue.createApp({
    components: {
        SelectSection,
        AssessmentTable,
        StudentTable,
        GradeDistributionTable
    },
    data() {
        return {
            sections: [],
            selectedSection: "",
            showStudents: true,
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