import { SelectSection } from "./components/select_section.js";

const StudentCLOTable = {
    props: ["clos", "student"],
    template: `
        <div class="table-striped table-responsive" style="white-space: nowrap">
            <table class="table table-bordered text-center">
                <!-- Table Head -->
                <thead class="text-white thead-dark">
                    <!-- CLO Headers -->
                    <tr>
                        <th rowspan="4">SAP ID</th>
                        <th rowspan="4">Student Name</th>
                        <th v-for="clo in clos" :colspan="getCLOColSpan(clo)" class="align-middle">
                            {{ clo.clo_id }} ({{ clo.weightage }}%)
                        </th>
                        <th rowspan="4" class="align-middle">Total CLOs Weightage</th>
                    </tr>
                    <!-- Assessment Types Headers -->
                    <tr>
                        <template v-for="clo in clos">
                            <th v-for="assessment in getAssessments(clo)" :colspan="2">
                                {{ assessment.charAt(0).toUpperCase() + assessment.slice(1) }}
                            </th>
                            <th rowspan="2" colspan="2" class="align-middle">Total</th>
                        </template>
                    </tr>
                    <!-- Marks, Percentage & Attainment Headers -->
                    <tr>
                        <template v-for="clo in clos">
                            <template v-for="assessment in getAssessments(clo)">
                                <th>Marks</th>
                                <th>Percentage %</th>
                            </template>
                        </template>
                    </tr>
                    <!-- Total Available Marks Row -->
                    <tr class="font-weight-bold bg-secondary text-white">
                        <template v-for="clo in clos">
                            <template v-for="assessment in getAssessments(clo)">
                                <th>{{ getTotalAvailableMarks(clo, assessment) }}</th>
                                <th>{{ getAssessmentWeightPercentage(clo, assessment) }}%</th>
                            </template>
                            <th class="bg-warning">{{ clo.totalMarks.toFixed(2) }}</th>
                            <th class="bg-info">{{ 100 }}%</th>
                        </template>
                    </tr>
                </thead>
                <!-- Table Body -->
                <tbody>
                    <tr>
                        <td>{{ student.sap_id }}</td>
                        <td>{{ student.student_details.first_name }} {{ student.student_details.last_name }}</td>
                        <template v-for="clo in clos">
                            <template v-for="assessment in getAssessments(clo)">
                                <td>{{ getObtainedScore(student, clo.clo_id, assessment) }}</td>
                                <td>{{ getStudentPercentage(student, clo, assessment) }}%</td>
                            </template>
                            <td class="font-weight-bold">{{ getTotalCLOScore(student, clo.clo_id) }}</td>
                            <td class="font-weight-bold">{{ getAttainmentPercentage(student, clo) }}%</td>
                        </template>
                        <td class="bg-primary text-white font-weight-bold">{{ getTotalWeightage(student) }}</td>
                    </tr>
                    <!-- Overall Attainment Row -->
                    <tr class="font-weight-bold bg-light">
                        <td colspan="2" class="text-right">Overall Attainment:</td>
                        <template v-for="clo in clos">
                            <template v-for="assessment in getAssessments(clo)">
                                <td>-</td>
                                <td>-</td>
                            </template>
                            <td>-</td>
                            <td class="bg-success text-white">{{ getOverallAttainment(clo) }}%</td>
                        </template>
                        <td>-</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,
    methods: {
        getAssessments(clo) {
            return Object.keys(clo.assessmentTypeContribution || {});
        },
        getCLOColSpan(clo) {
            return (this.getAssessments(clo).length * 2) + 2;
        },
        getTotalAvailableMarks(clo, assessment) {
            return clo.assessmentTypeContribution?.[assessment]?.toFixed(2) || "-";
        },
        getAssessmentWeightPercentage(clo, assessment) {
            let totalCLOMarks = parseFloat(clo.totalMarks) || 1;
            let assessmentMarks = parseFloat(clo.assessmentTypeContribution?.[assessment] || 0);
            return ((assessmentMarks / totalCLOMarks) * 100).toFixed(2);
        },
        getObtainedScore(student, cloId, assessment) {
            return student.clo_results?.[cloId]?.[assessment] ? student.clo_results[cloId][assessment].toFixed(2) : "-";
        },
        getStudentPercentage(student, clo, assessment) {
            let obtained = parseFloat(student.clo_results?.[clo.clo_id]?.[assessment] || 0);
            let totalAssessmentMarks = parseFloat(clo.assessmentTypeContribution?.[assessment] || 1);
            let assessmentWeightPercentage = this.getAssessmentWeightPercentage(clo, assessment);
            
            if (totalAssessmentMarks > 0) {
                return ((obtained / totalAssessmentMarks) * assessmentWeightPercentage).toFixed(2);
            }
            return "-";
        },
        getTotalCLOScore(student, cloId) {
            let total = 0;
            Object.values(student.clo_results?.[cloId] || {}).forEach(value => {
                total += parseFloat(value || 0);
            });
            return total.toFixed(2);
        },
        getAttainmentPercentage(student, clo) {
            let studentTotal = parseFloat(this.getTotalCLOScore(student, clo.clo_id)) || 0;
            let totalCLOMarks = parseFloat(clo.totalMarks) || 1;
            return ((studentTotal / totalCLOMarks) * 100).toFixed(2);
        },
        getOverallAttainment(clo) {
            return this.getAttainmentPercentage(this.student, clo);
        },
        getTotalWeightage(student) {
            let total = 0;
            Object.keys(student.clo_results || {}).forEach(cloId => {
                Object.values(student.clo_results[cloId] || {}).forEach(value => {
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
            dataLoaded: false,
            clos: [],
            student: {}
        };
    },
    components: {
        "select-section": SelectSection,
        "student-clo-table": StudentCLOTable
    },
    watch: {
        selectedSection(newSection) {
            if (newSection) {
                this.fetchSectionData();
            }
        }
    },
    methods: {
        async fetchSections() {
            try {
                let response = await fetch('/api/sections/');
                let data = await response.json();
                this.sections = data.sections;
                if (this.sections.length > 0) {
                    this.selectedSection = this.sections[0].id;  // ✅ Automatically select the first section
                    this.fetchSectionData();
                }
            } catch (error) {
                console.error("Error fetching sections:", error);
            }
        },
        async fetchSectionData() {
            if (!this.selectedSection) return;

            let apiUrl = `/api/student/section/${this.selectedSection}/clo_result/`;  // ✅ Fix API URL usage
            try {
                let response = await fetch(apiUrl);
                let data = await response.json();
                if (data.status === "success") {
                    this.clos = data.data.CLOs || [];
                    this.student = data.data.student;
                    this.dataLoaded = true;
                }
            } catch (error) {
                console.error("Error fetching section data:", error);
            }
        },
    },
    mounted() {
        this.fetchSections();
    }
});

app.mount("#app");