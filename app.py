```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Container Loading & Salt Weight Calculator</title>
    <style>
        :root {
            --primary-color: #2c3e50;
            --accent-color: #d35400;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #333333;
            --border-radius: 8px;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }

        .calculator-container {
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            width: 100%;
            max-width: 600px;
            padding: 30px;
            box-sizing: border-box;
        }

        h2 {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 25px;
            font-size: 1.5rem;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 0.95rem;
        }

        select, input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: var(--border-radius);
            font-size: 1rem;
            box-sizing: border-box;
            transition: border-color 0.2s;
        }

        select:focus, input:focus {
            outline: none;
            border-color: var(--accent-color);
        }

        .row {
            display: flex;
            gap: 15px;
        }

        .row .form-group {
            flex: 1;
        }

        button {
            background-color: var(--accent-color);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            padding: 14px;
            font-size: 1rem;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
            transition: background-color 0.2s;
            margin-top: 10px;
        }

        button:hover {
            background-color: #b54600;
        }

        .results {
            margin-top: 30px;
            background-color: #f1f5f8;
            border-radius: var(--border-radius);
            padding: 20px;
            border-left: 5px solid var(--accent-color);
        }

        .results h3 {
            margin-top: 0;
            color: var(--primary-color);
            font-size: 1.2rem;
            margin-bottom: 15px;
        }

        .result-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 0.95rem;
        }

        .result-item span:last-child {
            font-weight: bold;
            color: var(--primary-color);
        }
    </style>
</head>
<body>

<div class="calculator-container">
    <h2>Himalayan Salt Container & Weight Calculator</h2>
    
    <div class="form-group">
        <label for="containerType">Container Size</label>
        <select id="containerType">
            <option value="20">20ft Container (Max Payload: 27,000 kg)</option>
            <option value="40" selected>40ft Container (Max Payload: 28,500 kg)</option>
        </select>
    </div>

    <div class="form-group">
        <label for="productType">Product Packaging</label>
        <select id="productType">
            <option value="25">25 kg PP Bags</option>
            <option value="50">50 kg PP Bags</option>
            <option value="10">10 kg Craft Boxes</option>
            <option value="1">1 kg Retail Packs</option>
        </select>
    </div>

    <div class="row">
        <div class="form-group">
            <label for="targetTons">Target Weight (Metric Tons)</label>
            <input type="number" id="targetTons" value="24" min="1" max="30" step="0.5">
        </div>
        <div class="form-group">
            <label for="palletized">Packing Method</label>
            <select id="palletized">
                <option value="loose">Loose Loaded (Floor)</option>
                <option value="palletized">Palletized</option>
            </select>
        </div>
    </div>

    <button onclick="calculateLoad()">Calculate Load</button>

    <div class="results" id="resultsSection">
        <h3>Calculation Summary</h3>
        <div class="result-item">
            <span>Total Weight:</span>
            <span id="resWeight">0 kg (0.00 MT)</span>
        </div>
        <div class="result-item">
            <span>Total Units Required:</span>
            <span id="resUnits">0 packs</span>
        </div>
        <div class="result-item">
            <span>Estimated Pallets:</span>
            <span id="resPallets">N/A</span>
        </div>
        <div class="result-item">
            <span>Container Capacity Used:</span>
            <span id="resCapacity">0%</span>
        </div>
    </div>
</div>

<script>
function calculateLoad() {
    const containerType = document.getElementById('containerType').value;
    const unitWeight = parseFloat(document.getElementById('productType').value);
    const targetTons = parseFloat(document.getElementById('targetTons').value);
    const packingMethod = document.getElementById('palletized').value;

    const maxPayload = containerType === '20' ? 27000 : 28500; // in kg
    const targetKg = targetTons * 1000;

    // Validation checks
    const finalKg = targetKg > maxPayload ? maxPayload : targetKg;
    const totalUnits = Math.round(finalKg / unitWeight);
    
    let estimatedPallets = "N/A";
    if (packingMethod === 'palletized') {
        // Standard assumption: ~1000kg to 1200kg per pallet for salt
        estimatedPallets = Math.ceil(finalKg / 1100);
    }

    const capacityUsed = ((finalKg / maxPayload) * 100).toFixed(1);

    // Update DOM
    document.getElementById('resWeight').innerText = `${finalKg.toLocaleString()} kg (${(finalKg/1000).toFixed(2)} MT)`;
    document.getElementById('resUnits').innerText = `${totalUnits.toLocaleString()} units`;
    document.getElementById('resPallets').innerText = packingMethod === 'palletized' ? `${estimatedPallets} Pallets` : 'Floor Loaded';
    document.getElementById('resCapacity').innerText = `${capacityUsed}% of max payload`;
}

// Run initial calculation on load
calculateLoad();
</script>

</body>
</html>

```
