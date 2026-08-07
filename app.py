<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Salt Weight & Container Loading Calculator</title>
    <style>
        :root {
            --primary: #d97706;
            --primary-dark: #b45309;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --border-color: #cbd5e1;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }

        h2 {
            margin-top: 0;
            color: var(--primary-dark);
            text-align: center;
            margin-bottom: 25px;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        label {
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }

        select, input {
            padding: 10px 12px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
        }

        select:focus, input:focus {
            border-color: var(--primary);
        }

        .btn-container {
            text-align: center;
            margin-bottom: 30px;
        }

        button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 12px 25px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        button:hover {
            background-color: var(--primary-dark);
        }

        .results-section {
            background: #f1f5f9;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid var(--primary);
        }

        .results-section h3 {
            margin-top: 0;
            margin-bottom: 15px;
        }

        .result-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 1.05rem;
        }

        .progress-bar-container {
            background: #e2e8f0;
            border-radius: 4px;
            height: 16px;
            width: 100%;
            margin-top: 5px;
            margin-bottom: 15px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            background-color: var(--primary);
            transition: width 0.4s ease, background-color 0.4s;
        }

        .warning {
            color: #dc2626;
            font-weight: bold;
            margin-top: 10px;
            display: none;
        }
    </style>
</head>
<body>

<div class="container">
    <h2>Himalayan Salt Container Loading Calculator</h2>
    
    <div class="form-grid">
        <div class="form-group">
            <label for="containerType">Select Container Type</label>
            <select id="containerType">
                <option value="20ft">20ft Standard (Max: 28,000 kg / 33 CBM)</option>
                <option value="40ft">40ft High Cube (Max: 29,000 kg / 68 CBM)</option>
            </select>
        </div>

        <div class="form-group">
            <label for="itemType">Product Category</label>
            <select id="itemType">
                <option value="edible">Edible Salt / Granules (High Density)</option>
                <option value="bricks">Salt Bricks / Tiles</option>
                <option value="lamps">Salt Lamps (Packed with boxes)</option>
            </select>
        </div>

        <div class="form-group">
            <label for="totalUnits">Total Quantity (Pieces / Bags / Cartons)</label>
            <input type="number" id="totalUnits" placeholder="e.g., 1000" min="1">
        </div>

        <div class="form-group">
            <label for="weightPerUnit">Average Weight per Unit (kg)</label>
            <input type="number" id="weightPerUnit" placeholder="e.g., 25" step="0.01" min="0.01">
        </div>

        <div class="form-group">
            <label for="cbmPerUnit">Volume per Unit / Carton (CBM)</label>
            <input type="number" id="cbmPerUnit" placeholder="e.g., 0.03" step="0.0001" min="0.0001">
        </div>
    </div>

    <div class="btn-container">
        <button onclick="calculateLoad()">Calculate Load</button>
    </div>

    <div class="results-section" id="results" style="display: none;">
        <h3>Loading Summary</h3>
        
        <div class="result-row">
            <span>Total Cargo Weight:</span>
            <strong id="resWeight">0 kg</strong>
        </div>
        <div>
            <small>Weight Capacity Used:</small>
            <div class="progress-bar-container">
                <div class="progress-bar" id="weightProgress"></div>
            </div>
        </div>

        <div class="result-row">
            <span>Total Cargo Volume:</span>
            <strong id="resVolume">0 CBM</strong>
        </div>
        <div>
            <small>Volume Capacity Used:</small>
            <div class="progress-bar-container">
                <div class="progress-bar" id="volumeProgress"></div>
            </div>
        </div>

        <div class="warning" id="capacityWarning">
            ⚠️ Warning: Cargo exceeds container limits in weight or volume! Please adjust your quantities.
        </div>
    </div>
</div>

<script>
    // Container specifications database
    const containers = {
        "20ft": { maxWeight: 28000, maxVolume: 33 },
        "40ft": { maxWeight: 29000, maxVolume: 68 }
    };

    function calculateLoad() {
        const containerChoice = document.getElementById('containerType').value;
        const totalUnits = parseFloat(document.getElementById('totalUnits').value) || 0;
        const weightPerUnit = parseFloat(document.getElementById('weightPerUnit').value) || 0;
        const cbmPerUnit = parseFloat(document.getElementById('cbmPerUnit').value) || 0;

        if (totalUnits <= 0 || weightPerUnit <= 0 || cbmPerUnit <= 0) {
            alert("Please enter valid positive numbers for all fields.");
            return;
        }

        const totalWeight = totalUnits * weightPerUnit;
        const totalVolume = totalUnits * cbmPerUnit;

        const container = containers[containerChoice];

        const weightPercent = (totalWeight / container.maxWeight) * 100;
        const volumePercent = (totalVolume / container.maxVolume) * 100;

        // Update UI Results
        document.getElementById('resWeight').innerText = totalWeight.toLocaleString() + " kg (Max: " + container.maxWeight.toLocaleString() + " kg)";
        document.getElementById('resVolume').innerText = totalVolume.toFixed(2) + " CBM (Max: " + container.maxVolume + " CBM)";

        const weightBar = document.getElementById('weightProgress');
        const volumeBar = document.getElementById('volumeProgress');

        weightBar.style.width = Math.min(weightPercent, 100) + "%";
        volumeBar.style.width = Math.min(volumePercent, 100) + "%";

        // Color coding progress bars based on load
        weightBar.style.backgroundColor = weightPercent > 100 ? "#dc2626" : "#d97706";
        volumeBar.style.backgroundColor = volumePercent > 100 ? "#dc2626" : "#d97706";

        const warningElement = document.getElementById('capacityWarning');
        if (weightPercent > 100 || volumePercent > 100) {
            warningElement.style.display = "block";
        } else {
            warningElement.style.display = "none";
        }

        document.getElementById('results').style.display = "block";
    }
</script>

</body>
</html>
