var myChart;
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");
window.onload = function () {
  var labels = [];

  var data = {
    labels: labels,
    datasets: [
      {
        label: "Выявлено людей с симптомами",
        backgroundColor: "rgb(40, 44, 52)",
        borderColor: "rgb(255, 99, 132)",
        data: [],
      },
    ],
  };

  var config = {
    type: "line",
    data: data,
    options: {},
  };

  myChart = new Chart(document.getElementById("myChart"), config);
  update_graph()
};

async function update_graph() {
  let response = await fetch("report_data");
  if (response.ok) {
    let json = await response.json();
    redraw(json);
  } else {
    alert("Не удаётся получить данные для обновления графика");
  }
}

function redraw(data) {
  labels = Object.keys(data);
  labels.pop();
  labels.pop();
  numbers = [];
  for (i of Object.values(data)) {
    numbers.push(i.sick_count);
  }

  myChart.data.labels = labels;
  myChart.data.datasets[0].data = numbers;
  myChart.data.datasets.forEach((dataset) => {
    dataset.data.push(data);
  });
  myChart.update();
  document.getElementById("yellow").innerText = data.all_count;
  document.getElementById("red").innerText = data.sick_count;
  current_day = labels.pop();
  for (symptom of Object.keys(data[current_day])) {
    if (symptom !== "sick_count" && symptom !== "isCalled") {
      document.getElementById(symptom).innerText = data[current_day][symptom];
    }
  }
}

async function show_table(arg) {
  let response = await fetch("report_symptom", {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: JSON.stringify(arg.children[1].id),
  });
  if (response.ok) {
    let json = await response.json();
    create_table(json);
  } else {
    alert("Не удаётся получить данные по симтому");
  }
}

function create_table(data) {
  console.log(data);
  if (data === null) {
    return;
  }
  headers = Object.keys(data[0]);
  // document.
  // for(row in data){
  //   document.createElement('tr')

  // }
  var cols = [];

  for (var i = 0; i < data.length; i++) {
    for (var k in data[i]) {
      if (cols.indexOf(k) === -1) {
        // Push all keys to the array
        cols.push(k);
      }
    }
  }

  // Create a table element
  var table = document.createElement("table");

  // Create table row tr element of a table
  var tr = table.insertRow(-1);

  for (var i = 0; i < cols.length; i++) {
    // Create the table header th element
    var theader = document.createElement("th");
    theader.innerHTML = cols[i];

    // Append columnName to the table row
    tr.appendChild(theader);
  }

  // Adding the data to the table
  for (var i = 0; i < data.length; i++) {
    // Create a new row
    trow = table.insertRow(-1);
    for (var j = 0; j < cols.length; j++) {
      var cell = trow.insertCell(-1);

      // Inserting the cell at particular place
      cell.innerHTML = data[i][cols[j]];
      //cell.style.transform = 'rotate(90deg)';
    }
  }

  // Add the newly created table containing json data
  var el = document.getElementById("table");
  el.innerHTML = "";
  el.appendChild(table);
}

setInterval(update_graph, 60000);
