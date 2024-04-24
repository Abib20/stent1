var count = 0;
var questions = [
  "high_temperature",
  "runny_nose",
  "no_smell",
  "weakness",
  "muscle_pain",
  "nausea",
  "cough",
  "dyspnea",
  "diarrhea",
  "vomiting",
  "isCalled",
  "GotPills",
  "send"
];

function getNextQuestion() {
  if (count < questions.length) {
    document.getElementById(questions[count]).style.display = "none";
    count++;
    document.getElementById(questions[count]).style.display = "";
  }
}

function showEndInfo() {
  alert("Данные успешно отправлены!")
}
