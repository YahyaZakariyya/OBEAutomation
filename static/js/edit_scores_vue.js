import { ScoreTable } from "./components/score_table.js";

const app = Vue.createApp({
    components: {
        ScoreTable,
    },
    data() {
        return {
            assessmentId: new URLSearchParams(window.location.search).get('id'),
            assessmentTitle: "",
            questions: [],
            students: [],
            scores: [],
            exportedMetadata: null, 
            errorMessage: "",
            successMessage: "",
            csrfToken: ""
        };
    },
    mounted() {
        this.fetchAssessmentData();
        this.getCsrfToken();
    },
    methods: {
        getCsrfToken() {
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfMeta) {
                this.csrfToken = csrfMeta.getAttribute("content");
            } else {
                console.error("CSRF token meta tag is missing!");
            }
        },

        async fetchAssessmentData() {
            try {
                const response = await fetch(`/api/assessment-marks/?id=${this.assessmentId}`);
                if (!response.ok) throw new Error("Failed to fetch data.");

                const data = await response.json();
                this.assessmentTitle = data.assessment_title;
                this.questions = data.questions.map((q, index) => ({
                    ...q, number: index + 1 
                }));
                this.students = data.students;
                this.scores = data.scores.map(score => ({ ...score })); 

            } catch (error) {
                this.errorMessage = error.message;
            }
        },

        triggerFileInput() {
            this.$refs.fileInput.click();
        },

        exportToExcel() {
            this.exportedMetadata = {
                questionCount: this.questions.length,
                questionIds: this.questions.map(q => q.id)
            };

            const wb = XLSX.utils.book_new();
            const wsData = [
                ["", ...this.questions.map(q => `Question ${q.number}`)], 
                ["Question IDs", ...this.questions.map(q => q.id)], 
                ["Total Marks", ...this.questions.map(q => q.marks)], 
                ...this.students.map(student => [
                    `${student.first_name} ${student.last_name} (${student.username})`,
                    ...this.questions.map(q => {
                        const score = this.scores.find(s => s.student_id === student.id && s.question_id === q.id);
                        return score ? score.marks_obtained : 0;
                    })
                ])
            ];

            const ws = XLSX.utils.aoa_to_sheet(wsData);
            ws["!rows"] = [{ hidden: false }, { hidden: true }]; // ✅ Hide Question IDs Row

            XLSX.utils.book_append_sheet(wb, ws, "Scores");
            XLSX.writeFile(wb, `assessment_${this.assessmentId}_scores.xlsx`);
        },

        async importFromExcel(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = async (e) => {
                const workbook = XLSX.read(e.target.result, { type: "binary" });
                const sheet = workbook.Sheets[workbook.SheetNames[0]];
                const data = XLSX.utils.sheet_to_json(sheet, { header: 1 });

                let newScores = [];
                const importedQuestionIds = data[1].slice(1); 

                if (JSON.stringify(importedQuestionIds) !== JSON.stringify(this.questions.map(q => q.id))) {
                    this.errorMessage = "Imported file does not match current assessment structure.";
                    return;
                }

                data.slice(3).forEach(row => {
                    const studentName = row[0]?.trim();
                    const student = this.students.find(s => 
                        `${s.first_name} ${s.last_name} (${s.username})` === studentName
                    );
                    if (student) {
                        row.slice(1).forEach((score, i) => {
                            if (typeof score !== "string") score = String(score);  // ✅ Convert non-strings to strings
                            score = score.trim();  // ✅ Ensure trim() doesn't break
                            const question = this.questions[i];
                            if (question) {
                                newScores.push({
                                    student_id: student.id,
                                    question_id: question.id,
                                    marks_obtained: parseFloat(score) || 0
                                });
                            }
                        });
                    }
                });

                if (newScores.length !== this.scores.length) {
                    this.errorMessage = "Imported file structure does not match.";
                    return;
                }

                this.scores = newScores;
                this.successMessage = "Scores imported successfully!";
            };
            reader.readAsBinaryString(file);
        },

        updateScore(updatedScore) {
            const index = this.scores.findIndex(s => 
                s.student_id === updatedScore.student_id &&
                s.question_id === updatedScore.question_id
            );
            if (index !== -1) {
                // ✅ Force Vue to detect changes in the scores array
                this.scores = this.scores.map((s, i) => 
                    i === index ? { ...s, marks_obtained: updatedScore.marks_obtained } : s
                );
            }
        },

        async submitScores() {
            this.errorMessage = ""; // ✅ Clear previous errors
            this.successMessage = ""; // ✅ Clear previous success messages
            
            if (!this.csrfToken) {
                this.errorMessage = "CSRF token is missing!";
                return;
            }

            if (this.scores.length === 0) {
                this.errorMessage = "No changes made. Modify a record before saving.";
                return;
            }

            const processedScores = this.scores.map(score => ({
                student_id: score.student_id,
                question_id: score.question_id,
                marks_obtained: parseFloat(score.marks_obtained) || 0.0  
            }));

            try {
                const response = await fetch(`/api/assessment-marks/?id=${this.assessmentId}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": this.csrfToken
                    },
                    credentials: "include",
                    body: JSON.stringify({ scores: processedScores }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.errors || "Failed to save scores.");
                }
                this.successMessage = "Scores updated successfully!";
                setTimeout(() => { this.successMessage = ""; }, 3000);
            } catch (error) {
                this.errorMessage = error.message;
            }
        }
    }
});

app.mount("#app");
