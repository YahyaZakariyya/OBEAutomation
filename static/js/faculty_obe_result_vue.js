import { SelectSection } from "./components/select_section.js";

const CLOTable = {
    props: ["clos", "assessments"],
    template: `
        <table class="table table-bordered text-center">
            <thead class="table-dark">
                <tr>
                    <th rowspan="2">CLO</th>
                    <th rowspan="2">Weightage</th>
                    <th rowspan="2">Total Marks</th>
                    <th colspan="4">Assessment Contributions</th>
                </tr>
                <tr>
                    <th v-for="assessment in assessments">{{ assessment }}</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="clo in clos" :key="clo.title">
                    <td>{{ clo.title }}</td>
                    <td>{{ clo.weightage }}%</td>
                    <td>{{ clo.totalMarks.toFixed(2) }}</td>
                    <td v-for="assessment in assessments">
                        {{ clo.assessmentTypeContribution[assessment] ? clo.assessmentTypeContribution[assessment].toFixed(2) + '%' : '-' }}
                    </td>
                </tr>
            </tbody>
        </table>
    `
};

const StudentTable = {
    props: ["students", "assessments"],
    template: `
        <div class="table-responsive">
            <table class="table table-bordered text-center">
                <thead class="table-dark">
                    <tr>
                        <th rowspan="2">Student Name</th>
                        <th v-for="assessment in assessments" :colspan="2">{{ assessment }}</th>
                        <th rowspan="2">Total</th>
                    </tr>
                    <tr>
                        <th v-for="assessment in assessments">Obtained</th>
                        <th v-for="assessment in assessments">Weightage</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(student, studentName) in students" :key="studentName">
                        <td>{{ studentName }}</td>
                        <td v-for="assessment in assessments">
                            {{ getObtainedScore(student, assessment) }}
                        </td>
                        <td v-for="assessment in assessments">
                            {{ getAdjustedScore(student, assessment) }}
                        </td>
                        <td>{{ getTotalScore(student) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,
    methods: {
        getObtainedScore(student, assessment) {
            let total = 0;
            Object.keys(student).forEach(clo => {
                if (student[clo][assessment]) {
                    total += parseFloat(student[clo][assessment] || 0);
                }
            });
            return total.toFixed(2);
        },
        getAdjustedScore(student, assessment) {
            // Adjusted Score Logic: Can be modified based on weightage calculation
            let total = this.getObtainedScore(student, assessment);
            return (total * 1).toFixed(2);  // Assuming 1x multiplier, update accordingly
        },
        getTotalScore(student) {
            let total = 0;
            Object.keys(student).forEach(clo => {
                Object.values(student[clo]).forEach(value => {
                    total += parseFloat(value || 0);
                });
            });
            return total.toFixed(2);
        }
    }
};


const app = Vue.createApp({
    data() {
        return {
            sections: [],
            selectedSection: "",
            showStudents: false,
            dataLoaded: false,
            clos: [],
            students: {},
            assessmentTypes: []
        };
    },
    components: {
        "select-section": SelectSection,
        "clo-table": CLOTable,
        "student-table": StudentTable
    },
    watch: {
        selectedSection(newSection) {
            if (newSection) {
                this.fetchSectionData();
            }
        },
        showStudents() {
            this.fetchSectionData();
        }
    },
    methods: {
        async fetchSections() {
            try {
                let response = await fetch('/api/sections/');
                let data = await response.json();
                this.sections = data;
            } catch (error) {
                console.error("Error fetching sections:", error);
            }
        },
        async fetchSectionData() {
            if (!this.selectedSection) return;

            let apiUrl = `/api/faculty/section/${this.selectedSection}/clo_result/`;

            try {
                let response = await fetch(apiUrl);
                let data = await response.json();
                if (data.status === "success") {
                    this.clos = data.data.CLOs || [];
                    this.students = this.formatStudents(data.data.students || {});
                    this.assessmentTypes = this.extractAssessmentTypes(data.data.CLOs, data.data.students);
                    this.dataLoaded = true;
                }
            } catch (error) {
                console.error("Error fetching section data:", error);
            }
        },
        formatStudents(rawStudents) {
            let formattedStudents = {};
            Object.keys(rawStudents).forEach(studentName => {
                let studentData = rawStudents[studentName];
                formattedStudents[studentName] = {
                    assessment_type_score: studentData.assessment_type_score || {},
                    adjusted_course_score: studentData.adjusted_course_score || 0
                };
            });
            return formattedStudents;
        },
        extractAssessmentTypes(clos, students) {
            const types = new Set();

            // Extract from CLOs
            clos.forEach(clo => {
                Object.keys(clo.assessmentTypeContribution).forEach(type => types.add(type));
            });

            // Extract from students
            Object.values(students).forEach(student => {
                if (student.assessment_type_score) {
                    Object.keys(student.assessment_type_score).forEach(type => types.add(type));
                }
            });

            return Array.from(types);
        }
    },
    mounted() {
        this.fetchSections();
    }
});

app.mount("#app");
