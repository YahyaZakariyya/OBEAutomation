export const ScoreTable = {
    props: ["questions", "students", "scores"],
    template: `
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th rowspan="2">Student</th>
                    <th v-for="(question, index) in questions">Question {{ index + 1 }} ({{ question.marks }})</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="student in students" :key="student.id">
                    <td>{{ student.first_name }} {{ student.last_name }} ({{ student.username }})</td>
                    <td v-for="question in questions" :key="question.id">
                        <input type="number" class="form-control"
                               v-model="studentScores[student.id][question.id]"
                               :min="0" :max="question.marks"
                               @input="validateAndUpdate(student.id, question.id, studentScores[student.id][question.id])">
                    </td>
                </tr>
            </tbody>
        </table>
    `,
    computed: {
        studentScores() {
            return this.students.reduce((acc, student) => {
                acc[student.id] = this.questions.reduce((qAcc, question) => {
                    const score = this.scores.find(s => s.student_id === student.id && s.question_id === question.id);
                    qAcc[question.id] = score ? score.marks_obtained : 0;
                    return qAcc;
                }, {});
                return acc;
            }, {});
        }
    },
    methods: {
        validateAndUpdate(studentId, questionId, marksObtained) {
            const maxMarks = this.questions.find(q => q.id === questionId).marks;
            if (marksObtained > maxMarks) {
                alert(`Marks cannot exceed ${maxMarks}!`);
                this.studentScores[studentId][questionId] = maxMarks;
            } else {
                this.$emit("update-score", { student_id: studentId, question_id: questionId, marks_obtained: marksObtained });
            }
        }
    }
};
