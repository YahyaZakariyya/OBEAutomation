import { SelectSection } from "./components/select_section.js"; 

const OverviewSection = {
    props: ["overview"],
    template: `
        <div class="mb-4 card shadow-sm p-4">
            <h5 class="mb-3">Student Results Overview</h5>
            <div class="row">
                <div class="col-md-6">
                    <p>Total Weight: <strong>{{ overview.total_weight }}</strong></p>
                    <p>Course Completion: <strong>{{ overview.course_completion.toFixed(2) }}%</strong></p>
                    <p>Student Overall Score: <strong>{{ overview.student_current_overall.toFixed(2) }}%</strong></p>
                </div>
                <div class="col-md-6">
                    <canvas ref="overviewChart" style="height: 300px"></canvas>
                </div>
            </div>
        </div>
    `,
    mounted() {
        this.renderChart();
    },
    watch: {
        overview: "renderChart"
    },
    methods: {
        renderChart() {
            if (!this.$refs.overviewChart || !this.overview.assessment_types) return;

            const ctx = this.$refs.overviewChart.getContext("2d");
            if (this.chart) this.chart.destroy();

            this.chart = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: this.overview.assessment_types.map(t => t.type),
                    datasets: [{
                        data: this.overview.assessment_types.map(t => t.allocated_weight),
                        backgroundColor: ['#FF6384', '#FF9F40', '#FFCD56', '#4BC0C0', '#36A2EB'],
                        borderColor: ['#FF6384', '#FF9F40', '#FFCD56', '#4BC0C0', '#36A2EB'],
                        borderWidth: 1
                    }]
                }
            });
        }
    }
};

const SummaryTable = {
    props: {
        assessments: {
            type: Array,
            default: () => []  // Ensures it's never undefined
        }
    },
    template: `
        <div class="card shadow-sm p-4 mb-4">
            <h5 class="mb-3">Final Summary</h5>
            <div class="table-responsive">
                <table class="table table-bordered text-center">
                    <thead class="thead-light">
                        <tr>
                            <th>Assessments</th>
                            <th>Titles</th>
                            <th>Total.M</th>
                            <th>Obt.M</th>
                            <th>Weightage</th>
                            <th>Adjusted.M</th>
                            <th>Total Weightage</th>
                            <th>Completed Weightage</th>
                            <th>Adjusted.Total.Obt.M</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="(type, idx) in assessments" :key="idx">
                            <template v-if="type.assessments && type.assessments.length">
                                <tr v-for="(a, index) in type.assessments" :key="index">
                                    <td v-if="index === 0" :rowspan="type.assessments.length">{{ type.type }}</td>
                                    <td>{{ a.title.charAt(0).toUpperCase() + a.title.slice(1) }}</td>
                                    <td>{{ a.total_marks }}</td>
                                    <td>{{ a.student_obtained_marks }}</td>
                                    <td>{{ a.assessment_weight*type.allocated_weight/100 }}</td>
                                    <td>{{ (a.adjusted_marks*(a.assessment_weight*type.allocated_weight/100)/a.assessment_weight).toFixed(2) }}</td>
                                    <td v-if="index === 0" :rowspan="type.assessments.length">{{ type.allocated_weight }}</td>
                                    <td v-if="index === 0" :rowspan="type.assessments.length">{{ type.completion_percentage.toFixed(2) }}</td>
                                    <td v-if="index === 0" :rowspan="type.assessments.length">{{ type.adjusted_marks.toFixed(2) }}</td>
                                </tr>
                            </template>
                        </template>
                        <tr class="table-dark fw-bold">
                            <td colspan="6">Total</td>
                            <td>{{ totalWeight }}</td>
                            <td></td>
                            <td class="bg-danger">{{ totalScore }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `,
    computed: {
        totalScore() {
            return this.assessments.reduce((sum, type) => sum + (type.adjusted_marks || 0), 0).toFixed(2);
        },
        totalWeight() {
            return this.assessments.reduce((sum, type) => sum + (type.allocated_weight || 0), 0);
        }
    }
};

const app = Vue.createApp({
    components: { SelectSection, OverviewSection, SummaryTable },
    data() {
        return {
            sections: [],
            selectedSection: "",
            overviewData: null,
            majorData: []
        };
    },
    watch: {
        selectedSection(newVal) {
            if (newVal) this.fetchData(newVal);
        }
    },
    methods: {
        fetchSections() {
            fetch('/api/sections/')
                .then(res => res.json())
                .then(data => this.sections = data)
                .catch(err => console.error("Error fetching sections:", err));
        },
        fetchData(sectionId) {
            fetch(`/api/results/?section_id=${sectionId}`)
                .then(res => res.json())
                .then(data => {
                    this.overviewData = data;
                    this.majorData = data.assessment_types || [];
                })
                .catch(err => console.error("Error fetching data:", err));
        },
        downloadCSV() {
            let csv = "Types,Titles,Obt.M,Total.M,Adjusted.M,Weightage,Completed Weightage,Adjusted Obt.M,Total Weightage\n";
            this.majorData.forEach(type => {
                type.assessments.forEach(a => {
                    csv += `${type.type},${a.title},${a.student_obtained_marks},${a.total_marks},${a.adjusted_marks},${a.assessment_weight},${type.completion_percentage},${type.adjusted_marks},${type.allocated_weight}\n`;
                });
            });

            const blob = new Blob([csv], { type: "text/csv" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "student_results.csv";
            link.click();
        }
    },
    mounted() {
        this.fetchSections();
    }
});

app.mount("#app");
