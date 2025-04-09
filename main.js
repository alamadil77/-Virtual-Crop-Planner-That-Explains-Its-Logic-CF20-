const cropImages = {
      Tomato: "https://images2.alphacoders.com/110/thumb-1920-1106600.jpg",
      Rice: "https://www.learnreligions.com/thmb/5VvWl15le3qQhn33Pu2K0qoh26k=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/GettyImages-682901474-5c6450dcc9e77c0001566eab.jpg",
      Carrot: "https://i5.walmartimages.com/seo/Tendersweet-Carrot-Seeds-5-Lb-Non-GMO-Heirloom-Vegetable-Garden-Seeds-Gardening-by-Mountain-Valley-Seeds_e66fb972-b06a-4e45-bde6-a20a07f466a4_1.1885534e934f61f2cca9f3e15535ce53.jpeg",
      Cotton: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjWYmW9pgI_y_NDCxGs6lB8LpSZbe8MEnmIiA410lPjOCHW8fPlsW1vld1Q-_ol5-X_RIia4G9jUP8-TJEC9rpNmbWQy4lQem4CsC37DDdXZ70ZUiyLEhVhTJoMg2F_RxW0qqMYjSdJxJs/s400/Cotton.jpg",
      Maize: "https://bolbel.com/wp-content/uploads/2018/06/Maize.jpg"
    };

    function getRecommendation() {
      const soil = document.getElementById("soil").value;
      const season = document.getElementById("season").value;
      const output = document.getElementById("output");

      if (!soil || !season) {
        output.innerHTML = "⚠ Please select both soil and season.";
        return;
      }

      let crop = "";
      let reason = "";

      if (soil === "Loamy" && season === "Summer") {
        crop = "Tomato";
        reason = "Loamy soil is rich in nutrients and tomatoes thrive in summer heat.";
      } else if (soil === "Clay" && season === "Monsoon") {
        crop = "Rice";
        reason = "Clay retains water, perfect for water-loving rice in the rainy season.";
      } else if (soil === "Sandy" && season === "Winter") {
        crop = "Carrot";
        reason = "Carrots love the drainage of sandy soil and the cool of winter.";
      } else if (soil === "Black" && season === "Monsoon") {
        crop = "Cotton";
        reason = "Black soil holds moisture well, which cotton needs in monsoon.";
      } else {
        crop = "Maize";
        reason = "Maize is adaptable and fits your soil and season combination well.";
      }

      output.innerHTML = `
        <strong>Suggested Crop:</strong> ${crop}<br><br>
        <strong>Reason:</strong> ${reason}<br>
        <img class="crop-image" src="${cropImages[crop]}" alt="${crop}">
      `;

      updateChart(crop);
      fetchMarketPrice(crop);
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
            y: {
              beginAtZero: false
            }
          }
        }
      });
    }

    async function fetchMarketPrice(cropName) {
      const apiKey = "579b464db66ec23bdd0000017f070ea9c3d5432945f2974fe8d3133f";
      const resourceId = "9ef84268-d588-465a-a308-a864a43d0070";

      const url = `https://api.data.gov.in/resource/${resourceId}?api-key=${apiKey}&format=json&limit=5&filters[commodity]=${cropName}`;

      try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.records && data.records.length > 0) {
          const prices = data.records.map(item => (
            `${item.arrival_date} — ${item.market}: ₹${item.modal_price}/quintal`
          )).join("<br>");

          document.getElementById("output").innerHTML += `
            <br><br><strong>📈 Latest Real Market Prices:</strong><br>${prices}
          `;
        } else {
          document.getElementById("output").innerHTML += `
            <br><br><strong>No real-time price data available for ${cropName}.</strong>
          `;
        }
      } catch (error) {
        document.getElementById("output").innerHTML += `
          <br><br><strong>⚠ Could not fetch real prices. Check API key or network.</strong>
        `;
      }
    }

    function openHomeSlide() {
      document.getElementById("homeSlide").classList.add("active");
    }

    function closeHomeSlide() {
      document.getElementById("homeSlide").classList.remove("active");
    }