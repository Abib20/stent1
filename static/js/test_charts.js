let myChart;
let ChoosenDate = null;
let Today = null;
let four_buttons_data = new Map();
let json_file = null;
let excel_file = null;
let excel_file_url = null;
const request = (url, params = {}, method = 'GET') => {
    let options = {
        method
    };
    if ('GET' === method) {
        url += '?' + (new URLSearchParams(params)).toString();
    } else {
        options.body = JSON.stringify(params);
    }

    return fetch(url, options).then(response => response.json());
};

const get = (url, params) => request(url, params, 'GET');
const post = (url, params) => request(url, params, 'POST');

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
    let labels = [];

    let data = {
        labels: labels,
        datasets: [{
            label: "Выявлено людей с симптомами",
            backgroundColor: "rgb(40, 44, 52)",
            borderColor: "rgb(255, 99, 132)",
            data: [],
            tension: 0.5,
        }, ],
    };

    const ctx = document.getElementById("myChart").getContext('2d');
    myChart = new Chart(ctx, {
        type: "line",
        data: data,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            pointDotRadius: 6,
            pointDotStrokeWidth: 2,
            datasetStrokeWidth: 3,
            scaleShowVerticalLines: false,
            scaleGridLineWidth: 2,
            scaleShowGridLines: true,
            scaleGridLineColor: "rgba(225, 255, 255, 0.02)",
            scaleOverride: true,
            scaleSteps: 9,
            scaleStepWidth: 500,
            scaleStartValue: 0,

            responsive: true,
            onClick(e) {
                const points = myChart.getElementsAtEventForMode(e, 'nearest', {
                    intersect: true
                }, false)
                if (Array.isArray(points) && points.length) {
                    ChoosenDate = this.scales.x.ticks[points[0].index].label // выбранная дата в виде строки
                    update_numbers();
                    hide_table()
                }
            }
        }
    })
    update_graph()
};

async function update_numbers() {
    // узнаём сколько встречался каждый симптом в выбранную дату и обновляем значения что отображаются
    get("report_symptoms_count", {
        'date': ChoosenDate
    }).then(response => {
        redraw_symptoms_count(response)
    }, reason => {
        alert('Не удалось обновить информацию о количестве людей с каждым симптомом (Ошибка отображена в консоли)')
        console.log(reason)
    });
    // ASH => all sick health
    get('report_ASH_count', {
        'date': ChoosenDate
    }).then(response => {
        redraw_ASH_count(response)
    }, reason => {
        alert('Не удалось обновить информацию о количестве отчётов (Ошибка отображена в консоли)')
        console.log(reason)
    });
    // предзагрузка данных для кнопок
    get('without_reports', {
        'date': ChoosenDate
    }).then(response => {
        if (Array.isArray(response) && response.length) {
            four_buttons_data.set('without_reports', response)
            document.getElementById('without_reports').innerText = response.length;
        } else {
            four_buttons_data.set('without_reports', [])
            document.getElementById('without_reports').innerText = 0;
        }
    }, reason => {
        alert('Не удалось получить таблицу с пациентами не прошедшими опрос (Ошибка отображена в консоли)')
        console.log(reason)
    });
    get('uncalled_reports', {
        'date': ChoosenDate
    }).then(response => {
        if (Array.isArray(response) && response.length) {
            four_buttons_data.set('uncalled_reports', response)
            document.getElementById('uncalled_reports').innerText = response.length;
        } else {
            four_buttons_data.set('uncalled_reports', [])
            document.getElementById('uncalled_reports').innerText = 0;
        }
    }, reason => {
        alert('Не удалось получить таблицу с необзвонеными пациентами (Ошибка отображена в консоли)')
        console.log(reason)
    });
    get('reports_more_three', {
        'date': ChoosenDate
    }).then(response => {
        if (Array.isArray(response) && response.length) {
            four_buttons_data.set('reports_more_three', response)
            document.getElementById('reports_more_three').innerText = response.length;
        } else {
            four_buttons_data.set('reports_more_three', [])
            document.getElementById('reports_more_three').innerText = 0;
        }
    }, reason => {
        alert('Не удалось получить отчёты с более чем 3 симптомами (Ошибка отображена в консоли)')
        console.log(reason)
    });
    get('reports_symptom_three_days', {
        'date': ChoosenDate
    }).then(response => {
        if (Array.isArray(response) && response.length) {
            four_buttons_data.set('reports_more_three_days', response)
            document.getElementById('reports_more_three_days').innerText = response.length;
        } else {
            four_buttons_data.set('reports_more_three_days', [])
            document.getElementById('reports_more_three_days').innerText = 0;
        }
    }, reason => {
        alert('Не удалось получить отчёты с симптомами 3 дня подряд (Ошибка отображена в консоли)')
        console.log(reason)
    });
}

async function show_reports_table(button) {
    data = four_buttons_data.get(button);
    if (data.length !== 0) {
        create_table(four_buttons_data.get(button));
    } else {
        hide_table()
    }

}

function redraw_symptoms_count(symptoms_count) {
    for (symptom in symptoms_count) {
        document.getElementById(symptom).innerText = symptoms_count[symptom];
    }
}

async function get_all_reports() {
    get("report_all", {
        'date': ChoosenDate
    }).then(response => {
        if (Array.isArray(response) && response.length) {
            create_table(response)
        } else {
            alert('За выбранную дату отчётов не обнаружено!')
        }
    }, reason => {
        alert('Не удалось получить информацию о всех отчётах за выбранную дату (Ошибка отображена в консоли)')
        console.log(reason)
    });
}

async function get_health_reports() {
    get("report_health", {
        'date': ChoosenDate
    }).then(response => {
        if (Array.isArray(response) && response.length) {
            create_table(response)
        } else {
            alert('За выбранную дату безсимптомных отчётов не обнаружено!')
        }
    }, reason => {
        alert('Не удалось обновить информацию о безсимптомных отчётах за выбранную дату (Ошибка отображена в консоли)')
        console.log(reason)
    });
}

async function get_sick_reports() {
    get("report_sick", {
        'date': ChoosenDate
    }).then(response => {
        if (Array.isArray(response) && response.length) {
            create_table(response)
        } else {
            alert('За выбранную дату отчётов с симптомами не обнаружено!')
        }
    }, reason => {
        alert('Не удалось обновить информацию о отчётах с симтомами за выбранную дату (Ошибка отображена в консоли)')
        console.log(reason)
    });
}

function redraw_ASH_count(ASH) {
    document.getElementById("all").innerText = ASH.all;
    document.getElementById("health").innerText = ASH.health;
    document.getElementById("sick").innerText = ASH.sick;
}

async function get_symptom_table(arg) {
    get('report_symptom', {
        'symptom': arg,
        'date': ChoosenDate
    }).then(response => {
        create_table(response)
    }, reason => {
        alert('Не удалось получить таблицу с пациентами выбранного симптома (Ошибка отображена в консоли)')
        console.log(reason)
    });
}

async function update_graph() {
    scales = myChart.scales.x.ticks
    get('report_data1', {
        'Today': Today
    }).then(response => {
        Today = Today === Object.keys(response).pop() ? Today : Object.keys(response).pop();
        ChoosenDate = ChoosenDate === null ? Today : ChoosenDate;
        update_numbers();
        fill_graph(response);
    }, reason => {
        alert('Не удалось обновить график (Ошибка отображена в консоли)')
        console.log(reason)
    })
}

function fill_graph(data) {
    myChart.data.labels = Object.keys(data); // ставим даты
    myChart.data.datasets[0].data = Object.values(data); // ставим линию
    myChart.update(); // обновляем картинку
}

async function download_excel_file(data) {
    json_file = data
    let response = await fetch("download_excel_file/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken
        },
        mode: "same-origin",
        body: JSON.stringify(data),
    });
    if (response.ok) {
        response.blob().then(response => {
            excel_file = response;
            excel_file_url = window.URL.createObjectURL(response);
        })
    } else {
        alert("Не удаётся получить excel файл");
    }
}
// need to moderate for nicier view
function create_table(data) {
    if (data === null) {
        return;
    }
    download_excel_file(data);
    document.getElementById("df_button").disabled = false
    headers = Object.keys(data[0]);
    let cols = [];

    for (let i = 0; i < data.length; i++) {
        for (let k in data[i]) {
            if (cols.indexOf(k) === -1) {
                // Push all keys to the array
                cols.push(k);
            }
        }
    }

    // Create a table element
    let table = document.createElement("table");

    // Create table row tr element of a table
    let tr = table.insertRow(-1);

    for (let i = 0; i < cols.length; i++) {
        // Create the table header th element
        let theader = document.createElement("th");
        theader.innerHTML = cols[i];

        // Append columnName to the table row
        tr.appendChild(theader);
    }

    // Adding the data to the table
    for (let i = 0; i < data.length; i++) {
        // Create a new row
        trow = table.insertRow(-1);
        for (let j = 0; j < cols.length; j++) {
            let cell = trow.insertCell(-1);

            // Inserting the cell at particular place
            cell.innerHTML = data[i][cols[j]];
            //cell.style.transform = 'rotate(90deg)';
        }
    }

    // Add the newly created table containing json data
    let el = document.getElementById("table");
    el.innerHTML = "";
    el.appendChild(table);
}

function hide_table() {
    table = document.getElementById("table")
    while (table.firstChild) {
        table.removeChild(table.firstChild);
    }
}

function download_file() {
    window.open(excel_file_url);
}

setInterval(update_graph, 15000);