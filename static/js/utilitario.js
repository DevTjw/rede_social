// =========================
// 📌 utilitario.js
// Funções para interações da página: 
// - Menu lateral
// - Cálculos (MMC, raiz quadrada, IMC)
// - Integração com YouTube
// - APIs: Clima (OpenWeather) e Moedas (Open Exchange Rates)
// =========================

// 🔹 Espera o DOM carregar para executar jQuery
$(document).ready(function () {

    // 👉 Alterna a exibição do menu lateral
    $('#menuToggle').click(function () {
        $('#sidebar').toggleClass('show');
    });

    // 👉 Calcula o MMC entre dois números
    $('#btn-mmc').click(function () {
        let a = parseInt($('#num1').val()), b = parseInt($('#num2').val());
        if (isNaN(a) || isNaN(b)) 
            return $('#mmc-result').text('Insira dois números válidos.');

        let max = Math.max(a, b);
        while (true) {
            if (max % a === 0 && max % b === 0) {
                $('#mmc-result').text('MMC: ' + max);
                return;
            }
            max++;
        }
    });

    // 👉 Calcula a raiz quadrada de um número
    $('#btn-calc').click(function () {
        let val = parseFloat($('#calc-input').val());
        if (isNaN(val)) 
            return $('#calc-result').text('Número inválido.');

        $('#calc-result').text('Resultado: ' + Math.sqrt(val));
    });

    // 👉 Calcula o IMC e retorna classificação
    $('#btn-imc').click(function () {
        let peso = parseFloat($('#peso').val()), altura = parseFloat($('#altura').val());
        if (!peso || !altura) return alert('Informe peso e altura válidos!');

        let imc = peso / (altura * altura), msg = '';
        if (imc < 18.5) msg = 'Baixo peso';
        else if (imc < 25) msg = 'Peso adequado';
        else if (imc < 30) msg = 'Sobrepeso';
        else msg = 'Obesidade';

        $('#resultadoIMC').text(`Seu IMC é ${imc.toFixed(2)} → ${msg}`);
    });

    // 👉 Embeda vídeo do YouTube a partir de uma URL
    $('#btn-yt').click(function () {
        const url = $('#youtube-url').val().trim();
        const match = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})/);

        if (!match) return alert('URL inválida!');
        const videoId = match[1];

        $('#youtube-video').html(`
            <iframe width="100%" height="315" 
                    src="https://www.youtube.com/embed/${videoId}" 
                    frameborder="0" allowfullscreen>
            </iframe>
        `);
    });

    // 👉 Consulta clima atual (API OpenWeatherMap)
    async function loadWeather() {
        try {
            const resp = await fetch('https://api.openweathermap.org/data/2.5/weather?q=São Paulo,BR&appid=YOUR_API_KEY&units=metric&lang=pt_br');
            const data = await resp.json();
            $('#weather-data').text(`🌡 ${data.main.temp}°C | ${data.weather[0].description}`);
        } catch (err) {
            $('#weather-data').text('Erro ao carregar clima');
        }
    }

    // 👉 Consulta cotações de moedas (API ExchangeRate)
    async function loadCurrency() {
        try {
            const resp = await fetch("https://open.er-api.com/v6/latest/BRL");
            const data = await resp.json();

            $("#usd").text(`R$ ${(1 / data.rates.USD).toFixed(2)}`);
            $("#eur").text(`R$ ${(1 / data.rates.EUR).toFixed(2)}`);
            $("#gbp").text(`R$ ${(1 / data.rates.GBP).toFixed(2)}`);
        } catch (err) {
            $("#currency-data").text("Erro ao carregar cotações");
        }
    }

    // 🔄 Atualiza cotações a cada 5 minutos
    setInterval(loadCurrency, 300000);
    loadCurrency();
    loadWeather();
});


// =========================
// 🌦️ API de Clima detalhada (OpenWeather)
// Inclui clima atual + previsão de 5 dias
// =========================
document.addEventListener("DOMContentLoaded", function () {
    const weatherData = document.getElementById("weather-data");
    const forecastDiv = document.getElementById("forecast");

    const apiKey = "7b381d5e49053b57b80cf77ba868cd6d"; // ⚠️ Substitua pela sua chave
    const city = "São Leopoldo";

    // URLs da API
    const currentUrl = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric&lang=pt_br`;
    const forecastUrl = `https://api.openweathermap.org/data/2.5/forecast?q=${city}&appid=${apiKey}&units=metric&lang=pt_br`;

    // Mapeamento dos ícones meteorológicos
    const iconMap = {
        "01d": "wi-day-sunny", "01n": "wi-night-clear",
        "02d": "wi-day-cloudy", "02n": "wi-night-alt-cloudy",
        "03d": "wi-cloud", "03n": "wi-cloud",
        "04d": "wi-cloudy", "04n": "wi-cloudy",
        "09d": "wi-showers", "09n": "wi-showers",
        "10d": "wi-day-rain", "10n": "wi-night-alt-rain",
        "11d": "wi-thunderstorm", "11n": "wi-thunderstorm",
        "13d": "wi-snow", "13n": "wi-snow",
        "50d": "wi-fog", "50n": "wi-fog"
    };

    // 👉 Carregar clima atual
    fetch(currentUrl)
        .then(response => response.json())
        .then(data => {
            if (data.cod === 200) {
                const temp = data.main.temp.toFixed(1);
                const description = data.weather[0].description;
                const icon = data.weather[0].icon;
                const iconClass = iconMap[icon] || "wi-na";

                weatherData.innerHTML = `
                    <i class="wi ${iconClass}" style="font-size:28px; color:#ff9800;"></i>
                    <b>${city}</b>: ${temp}°C, ${description}
                `;
            } else {
                weatherData.innerText = "Não foi possível carregar o clima.";
            }
        })
        .catch(() => weatherData.innerText = "Erro ao carregar dados do clima.");

    // 👉 Carregar previsão de 5 dias (meio-dia)
    fetch(forecastUrl)
        .then(response => response.json())
        .then(data => {
            if (data.cod === "200") {
                let forecastHTML = "<h6>Previsão</h6><ul>";
                const daily = data.list.filter(item => item.dt_txt.includes("12:00:00"));

                daily.forEach(item => {
                    const date = new Date(item.dt_txt).toLocaleDateString("pt-BR", {
                        weekday: "short",
                        day: "2-digit",
                        month: "2-digit"
                    });
                    const temp = item.main.temp.toFixed(1);
                    const description = item.weather[0].description;
                    const icon = item.weather[0].icon;
                    const iconClass = iconMap[icon] || "wi-na";

                    forecastHTML += `
                        <li>
                            ${date}:
                            <i class="wi ${iconClass}" style="font-size:20px; color:#2196f3;"></i>
                            ${temp}°C - ${description}
                        </li>
                    `;
                });

                forecastHTML += "</ul>";
                forecastDiv.innerHTML = forecastHTML;
            } else {
                forecastDiv.innerText = "Não foi possível carregar a previsão.";
            }
        })
        .catch(() => forecastDiv.innerText = "Erro ao carregar a previsão.");
});


// =========================
// 🎥 Função utilitária extra (YouTube)
// =========================
function getYouTubeEmbedURL(url) {
    const match = url.match(/(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})/);
    return match ? `https://www.youtube.com/embed/${match[1]}` : null;
}

$('#btn-yt').click(function () {
    const url = $('#youtube-url').val().trim();
    const embedURL = getYouTubeEmbedURL(url);

    if (!embedURL) return alert('URL inválida!');

    $('#youtube-video').html(`
      <iframe width="100%" height="315" 
              src="${embedURL}" 
              frameborder="0" allowfullscreen>
      </iframe>
    `);
});

document.addEventListener("DOMContentLoaded", function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const menuClose = document.querySelector('.menu-close');

    menuToggle.addEventListener('click', () => sidebar.classList.toggle('show'));
    if(menuClose){
        menuClose.addEventListener('click', () => sidebar.classList.remove('show'));
    }

    // Fecha sidebar clicando fora
    document.addEventListener('click', function(e){
        if(!sidebar.contains(e.target) && !menuToggle.contains(e.target)){
            sidebar.classList.remove('show');
        }
    });
});