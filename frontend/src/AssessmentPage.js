import React, { useState, useEffect } from 'react';

function AssessmentPage() {
  // Extract assessment_id from query params
  const params = new URLSearchParams(window.location.search);
  const assessmentId = params.get('id');

  const [questions, setQuestions] = useState([]);
  const [students, setStudents] = useState([]);
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch data on mount
  useEffect(() => {
    if (assessmentId) {
      fetch(`/api/get-assessment-data/?id=${assessmentId}`, {
        credentials: 'include' // Important for session auth
      })
        .then(res => res.json())
        .then(data => {
          setQuestions(data.questions);
          setStudents(data.students);

          // We receive scores as an array of {student_id, question_id, score}
          // We'll convert it into a structure that allows easy editing.
          // For example, a dictionary keyed by student_id, then question_id.
          const scoreMap = {};
          data.scores.forEach(s => {
            if (!scoreMap[s.student_id]) {
              scoreMap[s.student_id] = {};
            }
            scoreMap[s.student_id][s.question_id] = s.score;
          });
          setScores(scoreMap);
          setLoading(false);
        })
        .catch(err => console.error(err));
    }
  }, [assessmentId]);

  if (!assessmentId) {
    return <div>No assessment ID provided.</div>;
  }

  if (loading) {
    return <div>Loading data...</div>;
  }

  // Handle changes to a score cell
  const handleScoreChange = (studentId, questionId, newValue) => {
    setScores(prev => ({
      ...prev,
      [studentId]: {
        ...prev[studentId],
        [questionId]: newValue
      }
    }));
  };

  // Save scores
  const saveScores = () => {
    // Convert scores back to a simple array:
    // [{ student_id, question_id, score }, ...]
    const updatedScores = [];
    for (const studentId in scores) {
      for (const questionId in scores[studentId]) {
        updatedScores.push({
          student_id: parseInt(studentId),
          question_id: parseInt(questionId),
          score: parseFloat(scores[studentId][questionId])
        });
      }
    }

    fetch('/api/update-scores/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ scores: updatedScores })
    })
      .then(res => res.json())
      .then(resp => {
        if (resp.status === 'success') {
          alert('Scores updated successfully!');
        } else {
          alert('Error updating scores.');
        }
      })
      .catch(err => console.error(err));
  };

  // Render a table:
  // Columns: Student Name, then one column per question
  return (
    <div>
      <h1>Assessment ID: {assessmentId}</h1>
      <table border="1" cellPadding="5" cellSpacing="0">
        <thead>
          <tr>
            <th>Student</th>
            {questions.map(q => (
              <th key={q.id}>{q.question_text}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {students.map(stu => (
            <tr key={stu.id}>
              <td>{stu.username} ({stu.first_name} {stu.last_name})</td>
              {questions.map(q => (
                <td key={q.id}>
                  <input
                    type="number"
                    value={scores[stu.id] && scores[stu.id][q.id] !== undefined ? scores[stu.id][q.id] : 0}
                    onChange={e => handleScoreChange(stu.id, q.id, e.target.value)}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <button onClick={saveScores}>Save</button>
    </div>
  );
}

export default AssessmentPage;
