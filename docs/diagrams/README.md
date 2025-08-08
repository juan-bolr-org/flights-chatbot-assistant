# Architecture Diagrams

This directory contains individual Mermaid diagram files that can be converted to high-quality images (PNG, SVG, PDF) for presentations, documentation, and sharing with stakeholders.

## 📁 Diagram Files

| File | Description | Type |
|------|-------------|------|
| `01-system-architecture.mmd` | Overall system architecture showing Frontend, Backend, and AI Services | Flow Chart |
| `02-api-architecture.mmd` | Detailed API architecture with repository pattern and service layers | Flow Chart |
| `03-repository-pattern.mmd` | Repository pattern implementation with dependency injection | Flow Chart |
| `04-authentication-flow.mmd` | JWT authentication and token refresh flow | Sequence Diagram |
| `05-chat-agent-workflow.mmd` | LangGraph agent workflow with tools and services | Flow Chart |
| `06-booking-flow.mmd` | Flight booking process through repository pattern | Sequence Diagram |
| `07-knowledge-base-generation.mmd` | Generative AI Integration Diagram | Flow Diagram |
| `08-flight-assistant-infra.png` | Infrastructure Diagram | Architecture Diagram |
| `09-flight-assistant-CICD.png` | CICD Flow Diagram | Flow Diagram |

## 🎨 Converting to Images

### Option 1: Online Converters (Recommended for Quick Use)

1. **Mermaid Live Editor** (Free, High Quality)
   - Visit: https://mermaid.live/
   - Copy and paste the content of any `.mmd` file
   - Click "Download" → Choose format (PNG, SVG, PDF)
   - Best quality for presentations

2. **GitHub Integration** (For Documentation)
   - GitHub automatically renders Mermaid in markdown files
   - Simply reference: ```mermaid [content] ```
   - Great for README files and GitHub Pages

### Option 2: Command Line Tools

If you have Node.js installed:

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Convert single diagram to PNG
mmdc -i 01-system-architecture.mmd -o 01-system-architecture.png

# Convert all diagrams to PNG
for file in *.mmd; do
    mmdc -i "$file" -o "${file%.mmd}.png"
done

# Convert to SVG (vector format, scalable)
mmdc -i 01-system-architecture.mmd -o 01-system-architecture.svg

# Convert to PDF
mmdc -i 01-system-architecture.mmd -o 01-system-architecture.pdf
```

### Option 3: VS Code Extension

1. Install "Mermaid Markdown Syntax Highlighting" extension
2. Install "Markdown Preview Mermaid Support" extension
3. Open any `.mmd` file and preview
4. Right-click preview → "Save as Image"

### Option 4: Docker (No Installation Required)

```bash
# Convert using Docker
docker run --rm -v $(pwd):/data minlag/mermaid-cli -i /data/01-system-architecture.mmd -o /data/01-system-architecture.png

# Batch convert all diagrams
docker run --rm -v $(pwd):/data minlag/mermaid-cli -i "/data/*.mmd" -o /data/
```

## 📐 Recommended Settings for Different Uses

### For Presentations (PowerPoint, Google Slides)
```bash
mmdc -i diagram.mmd -o diagram.png --width 1920 --height 1080 --backgroundColor white
```

### For Documentation (High DPI)
```bash
mmdc -i diagram.mmd -o diagram.png --scale 2 --backgroundColor transparent
```

### For Print Materials
```bash
mmdc -i diagram.mmd -o diagram.pdf --format pdf --width 1200 --height 800
```

### For Web Documentation
```bash
mmdc -i diagram.mmd -o diagram.svg --format svg
```

## 🎯 Usage Examples

### In Presentations
- **System Architecture**: Perfect overview slide for technical presentations
- **Repository Pattern**: Great for explaining clean architecture principles
- **Authentication Flow**: Security and session management explanation

### In Documentation
- **API Architecture**: Technical documentation for developers
- **Booking Flow**: Process documentation for business stakeholders
- **Chat Agent Workflow**: AI integration explanation

### For Stakeholders
- **System Architecture**: High-level overview without technical details
- **Authentication Flow**: Security assurance for compliance teams
- **Chat Agent Workflow**: AI capabilities demonstration

## 🔧 Customization Tips

### Colors and Themes
You can modify the color schemes in the `.mmd` files by changing the `fill` values:

```mermaid
style "Frontend" fill:#e1f5fe  // Light blue
style "Backend" fill:#f3e5f5   // Light purple
style "AI Services" fill:#e8f5e8  // Light green
```

### Font Sizes for Different Outputs
- **Large presentations**: Add `--scale 3` for bigger text
- **Small documentation**: Use default settings
- **Print materials**: Add `--scale 2` for crisp text

## 📋 Quick Conversion Commands

```bash
# Convert all diagrams to PNG for presentations
for file in *.mmd; do
    mmdc -i "$file" -o "images/${file%.mmd}.png" --width 1920 --height 1080 --backgroundColor white
done

# Convert all diagrams to SVG for web
for file in *.mmd; do
    mmdc -i "$file" -o "web/${file%.mmd}.svg"
done
```

## 🚀 Pro Tips

1. **Vector Formats (SVG)** are best for web and scalable documents
2. **PNG with high DPI** works great for presentations and print
3. **PDF format** is perfect for formal documentation
4. **White background** for presentations, **transparent** for documentation
5. **Test different scales** to find the perfect text size for your use case

## 📱 Mobile-Friendly Versions

For mobile documentation, consider creating simplified versions:
- Remove detailed labels
- Increase node sizes
- Use shorter text descriptions
- Focus on main flow rather than details

---

*These diagrams provide a complete visual representation of the Flights Chatbot Assistant architecture, from high-level system overview to detailed implementation patterns.*