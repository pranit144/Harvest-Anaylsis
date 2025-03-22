# Kisan Harvest Analyzer

## Overview
Kisan Harvest Analyzer is a web application designed to help farmers determine if their crops are ready for harvest. By uploading a photo of their plant along with details about the plant type, variety, and planting date, farmers receive an instant assessment of harvest readiness.

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference


## Features
- **Plant Image Analysis**: Upload photos of your crops for AI-powered harvest readiness assessment
- **Variety-Specific Analysis**: Select from common plant types and their specific varieties
- **Planting Date Tracking**: Factor in growing time by specifying when seeds were planted
- **Instant Results**: Get immediate feedback on whether your crop is ready to harvest
- **Mobile-Friendly Interface**: Use in the field on any device with a responsive design

## Technology Stack
- **Backend**: Python with Flask
- **AI**: Google Generative AI (Gemini 1.5 Flash)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Dependencies**: 
  - Flask
  - google-generativeai
  - Bootstrap (via CDN)
  - jQuery (via CDN)

## Installation

### Prerequisites
- Python 3.7+
- Google Generative AI API key

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/kisan-harvest-analyzer.git
   cd kisan-harvest-analyzer
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install flask google-generativeai
   ```

4. Set up your API key:
   - Replace the API key in the code with your own Google Generative AI API key
   - For production, use environment variables instead of hardcoding

## Usage

1. Start the application:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Use the application:
   - Select plant type from the dropdown
   - Choose variety/subcategory
   - Enter planting date
   - Upload a clear photo of your crop
   - Click "Check Harvest Readiness"
   - View the analysis results

## Deployment

### Docker
A Dockerfile is provided for containerized deployment:

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run the Docker container:
```
docker build -t kisan-harvest-analyzer .
docker run -p 5000:5000 kisan-harvest-analyzer
```

### Hugging Face Spaces
This project can be deployed on Hugging Face Spaces using the provided configuration.

## Future Enhancements
- Multi-language support for regional farmers
- Offline functionality for areas with limited connectivity
- Detailed harvest timing predictions with weather integration
- Plant disease detection alongside harvest readiness
- User accounts to track harvest history

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- Google for the Generative AI API
- Bootstrap team for the UI framework
- All contributors and testers who helped improve this tool


