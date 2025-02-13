import { ScoreTable } from "./components/score_table.js";

const app = Vue.createApp({
    components: {
        ScoreTable,
    },
    data() {
        return {
            assessmentId: new URLSearchParams(window.location.search).get('id'),
            questions: [],
            students: [],
            scores: [],
            errorMessage: "",
            successMessage: "",
            csrfToken: "" // ✅ CSRF token will be fetched later
        };
    },
    mounted() {
        this.fetchAssessmentData();
        this.getCsrfToken(); // ✅ Fetch CSRF token when DOM is ready
    },
    methods: {
        /** ✅ Fetch CSRF token from meta tag */
        getCsrfToken() {
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfMeta) {
                this.csrfToken = csrfMeta.getAttribute("content");
            } else {
                console.error("CSRF token meta tag is missing!");
            }
        },

        /** ✅ Fetch Questions, Students, and Scores from API */
        async fetchAssessmentData() {
            try {
                const response = await fetch(`/api/assessment-marks/?id=${this.assessmentId}`);
                if (!response.ok) throw new Error("Failed to fetch data.");
                
                const data = await response.json();
                this.questions = data.questions;
                this.students = data.students;
                this.scores = data.scores;
            } catch (error) {
                this.errorMessage = error.message;
            }
        },

        /** ✅ Update Score in Vue State */
        updateScore(updatedScore) {
            const index = this.scores.findIndex(s => 
                s.student_id === updatedScore.student_id &&
                s.question_id === updatedScore.question_id
            );
            if (index !== -1) {
                this.scores[index].marks_obtained = updatedScore.marks_obtained;
            } else {
                this.scores.push(updatedScore);
            }
        },

        /** ✅ Submit Scores to API with CSRF Protection */
        async submitScores() {
            if (!this.csrfToken) {
                this.errorMessage = "CSRF token is missing!";
                return;
            }

            try {
                const response = await fetch(`/api/assessment-marks/?id=${this.assessmentId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": this.csrfToken  // ✅ CSRF token included
                    },
                    credentials: "include", // ✅ Ensures cookies are sent
                    body: JSON.stringify({ scores: this.scores }),
                });
                console.log(scores)

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.errors || "Failed to save scores.");
                }
                this.successMessage = "Scores updated successfully!";
            } catch (error) {
                this.errorMessage = error.message;
            }
        },

        /** ✅ Export Data to Excel (CSV) */
        exportToExcel() {
            const csvContent = [
                ["Student", ...this.questions.map(q => `Question ${q.id}`)].join(","),
                ...this.students.map(student => [
                    `${student.first_name} ${student.last_name} (${student.username})`,
                    ...this.questions.map(q => {
                        const score = this.scores.find(s => s.student_id === student.id && s.question_id === q.id);
                        return score ? score.marks_obtained : 0;
                    })
                ].join(","))
            ].join("\n");

            const blob = new Blob([csvContent], { type: "text/csv" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `assessment_${this.assessmentId}_scores.csv`;
            link.click();
        },

        /** ✅ Handle File Upload */
        triggerFileInput() {
            this.$refs.fileInput.click();
        },

        /** ✅ Import Scores from Excel (CSV) */
        async importFromExcel(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = async (e) => {
                const csvData = e.target.result.split("\n").slice(1);
                let newScores = [];

                csvData.forEach(row => {
                    const values = row.split(",");
                    if (values.length > 1) {
                        const studentName = values[0].trim();
                        const student = this.students.find(s => 
                            `${s.first_name} ${s.last_name} (${s.username})` === studentName
                        );
                        if (student) {
                            values.slice(1).forEach((score, i) => {
                                const question = this.questions[i];
                                if (question) {
                                    newScores.push({
                                        student_id: student.id,
                                        question_id: question.id,
                                        marks_obtained: parseFloat(score.trim()) || 0
                                    });
                                }
                            });
                        }
                    }
                });

                // ✅ Ensure the file structure matches assessment
                if (newScores.length !== this.scores.length) {
                    this.errorMessage = "Imported file structure does not match.";
                    return;
                }

                this.scores = newScores;
                this.successMessage = "Scores imported successfully!";
            };
            reader.readAsText(file);
        }
    }
});

app.mount("#app");
