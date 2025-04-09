window.onload = () => {
  setTimeout(() => {
    document.getElementById('introScreen').classList.add('slide-up');
    document.getElementById('mainSite').classList.add('active');
  }, 1000);
  fetchWeatherAndFill();
};

function navigateTo(sectionId) {
  document.getElementById('home').style.display = 'none';
  document.getElementById('form').style.display = 'none';
  document.querySelector('.chart-container').style.display = 'none';
  document.querySelector('.price-table').style.display = 'none';
  document.querySelector('.info-section').style.display = 'none';
  document.querySelector('footer').style.display = 'none';

  if (sectionId === 'form') {
    document.getElementById('form').style.display = 'block';
    document.querySelector('.chart-container').style.display = 'block';
    document.querySelector('.price-table').style.display = 'block';
    document.querySelector('.info-section').style.display = 'block';
    document.querySelector('footer').style.display = 'block';
  } else if (sectionId === 'info') {
    document.querySelector('.info-section').style.display = 'block';
    document.querySelector('footer').style.display = 'block';
  } else {
    document.getElementById('home').style.display = 'block';
  }
}

async function fetchWeatherAndFill() {
  try {
    const position = await new Promise((resolve, reject) =>
      navigator.geolocation.getCurrentPosition(resolve, reject)
    );

    const { latitude, longitude } = position.coords;
    const apiKey = "eba3231896fa0aaf5affc93be31fcdd3";
    const url = `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${apiKey}&units=metric`;

    const res = await fetch(url);
    const data = await res.json();
    const temp = data.main.temp || 30;
    const rain = data.rain ? data.rain["1h"] || data.rain["3h"] || 0 : 0;

    document.getElementById("temperature").value = temp.toFixed(1);
    document.getElementById("rainfall").value = rain.toFixed(1);
  } catch (err) {
    console.error("Weather fetch error:", err);
  }
}

async function getRecommendation() {
  const soil = document.getElementById("soil").value;
  const season = document.getElementById("season").value;
  const rainfall = parseFloat(document.getElementById("rainfall").value);
  const temperature = parseFloat(document.getElementById("temperature").value);
  const outputDiv = document.getElementById("output");

  if (!soil || !season || isNaN(rainfall) || isNaN(temperature)) {
    outputDiv.innerHTML = `<p style="color:red;">Please fill all fields properly.</p>`;
    return;
  }

  const cropImages = {
    Tomato: "https://images2.alphacoders.com/110/thumb-1920-1106600.jpg",
    Rice: "https://www.learnreligions.com/thmb/5VvWl15le3qQhn33Pu2K0qoh26k=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/GettyImages-682901474-5c6450dcc9e77c0001566eab.jpg",
    Carrot: "https://i5.walmartimages.com/seo/Tendersweet-Carrot-Seeds-5-Lb-Non-GMO-Heirloom-Vegetable-Garden-Seeds-Gardening-by-Mountain-Valley-Seeds_e66fb972-b06a-4e45-bde6-a20a07f466a4_1.1885534e934f61f2cca9f3e15535ce53.jpeg",
    Cotton: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjWYmW9pgI_y_NDCxGs6lB8LpSZbe8MEnmIiA410lPjOCHW8fPlsW1vld1Q-_ol5-X_RIia4G9jUP8-TJEC9rpNmbWQy4lQem4CsC37DDdXZ70ZUiyLEhVhTJoMg2F_RxW0qqMYjSdJxJs/s400/Cotton.jpg",
    Maize: "https://bolbel.com/wp-content/uploads/2018/06/Maize.jpg"
  };

  try {
    const response = await fetch("http://localhost:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ soil, season, rainfall, temperature })
    });

    if (!response.ok) throw new Error("API unavailable");

    const data = await response.json();
    const crop = data.crop;

    outputDiv.innerHTML = `<h3>Recommended Crop: ${crop}</h3><img class="crop-image" src="${cropImages[crop] || ''}" alt="${crop}" />`;
    updateChart(crop);
    return;
  } catch (e) {
    console.warn("Using fallback rules:", e.message);
  }

  let crop = "Maize";
  if (soil === "Loamy" && season === "Summer" && temperature > 25) crop = "Tomato";
  else if (soil === "Clay" && season === "Monsoon" && rainfall > 150) crop = "Rice";
  else if (soil === "Sandy" && season === "Winter" && temperature < 20) crop = "Carrot";
  else if (soil === "Black" && season === "Monsoon") crop = "Cotton";

  outputDiv.innerHTML = `<h3>Recommended Crop: ${crop}</h3><img class="crop-image" src="${cropImages[crop] || ''}" alt="${crop}" />`;
  updateChart(crop);
}

function updateChart(crop) {
  const cropTrends = {
    Tomato: [20, 22, 25, 28],
    Rice: [32, 31, 30.5, 30],
    Carrot: [25, 30, 33, 35],
    Cotton: [45, 48, 50, 52],
    Maize: [18, 19, 19.5, 20]
  };

  const ctx = document.getElementById('trendChart').getContext('2d');
  if (window.myChart) window.myChart.destroy();
  window.myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr'],
      datasets: [{
        label: `${crop} Market Price (₹/kg)`,
        data: cropTrends[crop],
        borderColor: '#2d6a4f',
        backgroundColor: '#74c69d66',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: false }
      }
    }
  });
}
