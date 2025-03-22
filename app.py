import os
import base64
from flask import Flask, render_template_string, request, jsonify, flash, redirect, url_for
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "harvest_analyzer_secret_key"  # Required for flash messages

# Configure API key and generation parameters
genai.configure(api_key="AIzaSyCizcswP6vlKDMdB3HRAtVi2JbifOpbPvA")

GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create a global model instance
MODEL = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=GENERATION_CONFIG,
)

# List of common plants for selection
PLANT_LIST = [
    "Rice", "Wheat", "Maize", "Barley", "Sorghum", "Millets",
    "Pulses (Chickpea, Pigeon Pea, Mung Bean, etc.)", "Cotton", "Sugarcane",
    "Tea", "Coffee", "Potato", "Tomato", "Onion", "Garlic",
    "Brinjal (Eggplant)", "Okra", "Cucumber", "Carrot", "Lettuce",
    "Spinach", "Cabbage", "Cauliflower", "Peas", "Beans", "Ginger",
    "Turmeric", "Chili", "Mango", "Banana", "Apple", "Papaya",
    "Pomegranate", "Citrus", "Guava", "Melon", "Coconut", "Cashew",
    "Groundnut", "Soybean"
]

# HTML Template - Combined Base and Index template
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kisan Harvest Analyzer</title>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <!-- Custom CSS -->
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar {
            background-color: #2e7d32;
        }
        .navbar-brand {
            font-weight: bold;
            color: white !important;
        }
        .card {
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .btn-primary {
            background-color: #2e7d32;
            border-color: #2e7d32;
        }
        .btn-primary:hover {
            background-color: #1b5e20;
            border-color: #1b5e20;
        }
        .footer {
            background-color: #e8f5e9;
            padding: 15px 0;
            margin-top: 30px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .form-label {
            font-weight: 500;
            margin-top: 10px;
        }
        .plant-info {
            background-color: #e8f5e9;
            border-left: 4px solid #2e7d32;
            padding: 10px;
            margin-top: 15px;
        }
        .result-ready {
            background-color: #c8e6c9;
            border: 2px solid #2e7d32;
            color: #1b5e20;
            padding: 20px;
            border-radius: 8px;
            font-size: 1.2rem;
            text-align: center;
            margin: 20px 0;
        }
        .result-not-ready {
            background-color: #ffccbc;
            border: 2px solid #e64a19;
            color: #bf360c;
            padding: 20px;
            border-radius: 8px;
            font-size: 1.2rem;
            text-align: center;
            margin: 20px 0;
        }
        /* Adjustments for mobile devices */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            h1 {
                font-size: 1.8rem;
            }
        }
        .app-icon {
            background-color: #4CAF50;
            color: white;
            width: 30px;
            height: 30px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 5px;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">
                <span class="app-icon"><i class="bi bi-flower1"></i></span>
                Kisan Harvest Analyzer
            </a>
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-warning alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h3 class="mb-0">Harvest Readiness Check</h3>
                    </div>
                    <div class="card-body">
                        <div class="plant-info mb-4">
                            <p class="mb-0">Upload a photo of your crop to check if it's ready for harvest. Our system will analyze the plant's condition based on the variety and planting date.</p>
                        </div>

                        <form id="harvestForm" action="/assess" method="post" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="plant" class="form-label">Select Plant Type:</label>
                                <select class="form-select" id="plant" name="plant" required>
                                    <option value="" selected disabled>-- Choose Plant --</option>
                                    {% for plant in plants %}
                                        <option value="{{ plant }}">{{ plant }}</option>
                                    {% endfor %}
                                </select>
                            </div>

                            <div class="mb-3" id="subcategoryContainer" style="display: none;">
                                <label for="subcategory" class="form-label">Select Variety:</label>
                                <select class="form-select" id="subcategory" name="subcategory" required disabled>
                                    <option value="" selected disabled>-- First Select Plant Type --</option>
                                </select>
                                <div class="loading" id="subcategoryLoading">
                                    <div class="spinner-border text-success" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                    <p>Fetching varieties...</p>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label for="sowing_date" class="form-label">Planting Date:</label>
                                <input type="date" class="form-control" id="sowing_date" name="sowing_date" required>
                                <small class="text-muted">When did you sow/plant the seeds?</small>
                            </div>

                            <div class="mb-3">
                                <label for="image" class="form-label">Upload Plant Photo:</label>
                                <input type="file" class="form-control" id="image" name="image" accept="image/*" required>
                                <small class="text-muted">Take a clear photo of your plant/crop</small>

                                <div class="mt-3" id="imagePreview" style="display: none;">
                                    <p>Image Preview:</p>
                                    <img id="preview" src="#" alt="Preview" style="max-width: 100%; max-height: 300px;" class="rounded">
                                </div>
                            </div>

                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary" id="checkButton">Check Harvest Readiness</button>
                            </div>
                        </form>

                        <div class="loading" id="assessmentLoading">
                            <div class="spinner-border text-success" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p>Analyzing your crop... Please wait</p>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header bg-light">
                        <h4 class="mb-0">How to Use</h4>
                    </div>
                    <div class="card-body">
                        <ol>
                            <li>Select your plant type from the dropdown menu</li>
                            <li>Choose the specific variety of your plant</li>
                            <li>Enter the date when you planted the seeds</li>
                            <li>Take a clear photo of your plant and upload it</li>
                            <li>Click "Check Harvest Readiness" to get results</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="footer text-center mt-5">
        <div class="container">
            <p class="mb-0">© 2025 Kisan Harvest Analyzer - Helping farmers make informed decisions</p>
        </div>
    </footer>

    <!-- JavaScript dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    <script>
        // When plant selection changes, fetch subcategories
        $(document).ready(function() {
            // Show image preview when file is selected
            $("#image").change(function() {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        $("#preview").attr('src', e.target.result);
                        $("#imagePreview").show();
                    }
                    reader.readAsDataURL(file);
                }
            });

            // Fetch subcategories when plant is selected
            $("#plant").change(function() {
                const plant = $(this).val();
                if (plant) {
                    $("#subcategoryContainer").show();
                    $("#subcategoryLoading").show();
                    $("#subcategory").prop('disabled', true);

                    $.ajax({
                        url: '/get_subcategories',
                        type: 'POST',
                        data: {plant: plant},
                        success: function(response) {
                            $("#subcategory").empty();
                            const subcategories = response.subcategories;

                            subcategories.forEach(function(sub) {
                                $("#subcategory").append(new Option(sub, sub));
                            });

                            $("#subcategory").prop('disabled', false);
                            $("#subcategoryLoading").hide();
                        },
                        error: function() {
                            alert('Error fetching varieties. Please try again.');
                            $("#subcategoryLoading").hide();
                        }
                    });
                } else {
                    $("#subcategoryContainer").hide();
                }
            });

            // Show loading spinner on form submission
            $("#harvestForm").submit(function() {
                const isValid = this.checkValidity();
                if (isValid) {
                    $("#assessmentLoading").show();
                    $("#checkButton").prop('disabled', true);
                }
                return isValid;
            });
        });
    </script>
</body>
</html>
'''

# Results Template
RESULT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kisan Harvest Analyzer - Results</title>
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <!-- Custom CSS -->
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .navbar {
            background-color: #2e7d32;
        }
        .navbar-brand {
            font-weight: bold;
            color: white !important;
        }
        .card {
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .btn-primary {
            background-color: #2e7d32;
            border-color: #2e7d32;
        }
        .btn-primary:hover {
            background-color: #1b5e20;
            border-color: #1b5e20;
        }
        .footer {
            background-color: #e8f5e9;
            padding: 15px 0;
            margin-top: 30px;
        }
        .result-ready {
            background-color: #c8e6c9;
            border: 2px solid #2e7d32;
            color: #1b5e20;
            padding: 20px;
            border-radius: 8px;
            font-size: 1.2rem;
            text-align: center;
            margin: 20px 0;
        }
        .result-not-ready {
            background-color: #ffccbc;
            border: 2px solid #e64a19;
            color: #bf360c;
            padding: 20px;
            border-radius: 8px;
            font-size: 1.2rem;
            text-align: center;
            margin: 20px 0;
        }
        /* Adjustments for mobile devices */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            h1 {
                font-size: 1.8rem;
            }
        }
        .app-icon {
            background-color: #4CAF50;
            color: white;
            width: 30px;
            height: 30px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 5px;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">
                <span class="app-icon"><i class="bi bi-flower1"></i></span>
                Kisan Harvest Analyzer
            </a>
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-warning alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h3 class="mb-0">Harvest Analysis Results</h3>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-5">
                                <img src="data:image/jpeg;base64,{{ image_b64 }}" alt="Plant Image" class="img-fluid rounded">
                            </div>
                            <div class="col-md-7">
                                <h4>Your Crop Details:</h4>
                                <ul class="list-group mb-4">
                                    <li class="list-group-item"><strong>Plant Type:</strong> {{ plant }}</li>
                                    <li class="list-group-item"><strong>Variety:</strong> {{ subcategory }}</li>
                                    <li class="list-group-item"><strong>Planted on:</strong> {{ sowing_date }}</li>
                                </ul>

                                {% if is_ready %}
                                <div class="result-ready">
                                    <i class="bi bi-check-circle-fill"></i> {{ result }}
                                </div>
                                <p class="mt-3">Your crop shows the signs of maturity and is ready to be harvested. Plan your harvesting activities accordingly.</p>
                                {% else %}
                                <div class="result-not-ready">
                                    <i class="bi bi-x-circle-fill"></i> {{ result }}
                                </div>
                                <p class="mt-3">Your crop needs more time to mature. Continue caring for it and check again in a few days.</p>
                                {% endif %}
                            </div>
                        </div>

                        <div class="d-grid gap-2 mt-4">
                            <a href="/" class="btn btn-primary">Check Another Crop</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="footer text-center mt-5">
        <div class="container">
            <p class="mb-0">© 2025 Kisan Harvest Analyzer - Helping farmers make informed decisions</p>
        </div>
    </footer>

    <!-- JavaScript dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''


def fetch_subcategories(plant):
    """Fetch subcategories for the selected plant using Gemini."""
    prompt = f"List the subcategories or varieties of the plant '{plant}' as a comma-separated list."
    try:
        response = MODEL.generate_content(prompt)
        subs = [s.strip() for s in response.text.split(",") if s.strip()]
        return subs
    except Exception as e:
        print(f"Error fetching subcategories: {e}")
        return ["Error fetching varieties"]


def assess_harvest(plant, subcategory, sowing_date, image_b64):
    """
    Call Gemini to analyze harvest readiness using the provided inputs.
    The prompt instructs the model to output only one of:
      "Ready to harvest" or "Not ready to harvest".
    """
    truncated_img = image_b64[:100] + "...[truncated]"
    prompt = (
        f"Based on the following details, determine if the plant is ready to harvest. "
        f"Do not include any explanation; simply respond with either 'Ready to harvest' or 'Not ready to harvest'.\n\n"
        f"Plant: {plant}\n"
        f"Variety/Subcategory: {subcategory}\n"
        f"Sowing Date: {sowing_date}\n"
        f"Image (base64, truncated): {truncated_img}"
    )
    response = MODEL.generate_content(prompt)
    return response.text.strip()


@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE, plants=PLANT_LIST)


@app.route('/get_subcategories', methods=['POST'])
def get_subcategories():
    plant = request.form.get('plant')
    if not plant:
        return jsonify({"error": "No plant selected"}), 400

    subcategories = fetch_subcategories(plant)
    return jsonify({"subcategories": subcategories})


@app.route('/assess', methods=['POST'])
def assess():
    # Get form data
    plant = request.form.get('plant')
    subcategory = request.form.get('subcategory')
    sowing_date = request.form.get('sowing_date')

    # Validate inputs
    if not all([plant, subcategory, sowing_date]):
        flash("Please fill in all fields")
        return redirect(url_for('index'))

    # Validate date format
    try:
        datetime.strptime(sowing_date, "%Y-%m-%d")
    except ValueError:
        flash("Please enter a valid date in YYYY-MM-DD format")
        return redirect(url_for('index'))

    # Process image
    image = request.files.get('image')
    if not image:
        flash("Please upload an image of your plant")
        return redirect(url_for('index'))

    # Convert image to base64
    image_data = image.read()
    image_b64 = base64.b64encode(image_data).decode('utf-8')

    try:
        result = assess_harvest(plant, subcategory, sowing_date, image_b64)
        # Determine if ready for harvest to show appropriate styling
        is_ready = "ready" in result.lower()
        return render_template_string(
            RESULT_TEMPLATE,
            result=result,
            plant=plant,
            subcategory=subcategory,
            sowing_date=sowing_date,
            image_b64=image_b64,
            is_ready=is_ready
        )
    except Exception as e:
        flash(f"Error during assessment: {str(e)}")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)