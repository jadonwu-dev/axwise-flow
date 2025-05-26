# AxWise Presentation Website Documentation

This document provides an overview of the AxWise presentation website, its structure, and guidelines for updating it.

## Overview

The AxWise presentation website is a single-page presentation that showcases the AxWise product, a tool that bridges the gap between user insights and product development. The website is designed to be visually appealing, with consistent branding and animations to engage visitors.

The presentation is based on the original Google Slides presentation available at: [AxWise Presentation](https://docs.google.com/presentation/d/1aN4qEipmP5CQmVqp5g2iwr_MdQbcKcuggopgac3BNiw/edit#slide=id.p1)

## Structure

The website consists of the following sections:

1. **Hero**: Main branding and tagline
2. **Preamble**: Introduction from Vitalijs Visnevskis about the current state of tools
3. **Problem**: The bottleneck between conversation and code
   - Four key pain points: Research costs, Insight-to-Action Gap, Stakeholder Buy-in, and Wasted Development
   - Includes specific data points: "$50K-100K/year researchers" and "$260B/year wasted"
4. **Solution**: How AxWise simplifies user research
   - Highlights the simplicity: "The only input needed is your user interviews!"
   - Features three key capabilities: Advanced AI, Intuitive UI, and API-First architecture
   - Visual representation of data points extracted from interviews
   - **Description:** Outlines how AxWise solves the identified problems. It highlights key features and the type of data extracted from user interviews.
   - **Content:** Includes a subtitle, a section on data extraction with visual representation (`.data-visual`), a section for key features (`.features`), and an educational note emphasizing guidance on best practices.
   - **Styling:** Mint green background (`--mint-green`), centered text, specific styles for data points (`.data-point`), and highlighted data points (`.data-point-highlight`).
5. **Market Opportunity**: Market size and positioning
   - Visual transition from the smaller QDA market ($2B, "MEH") to the larger product development waste market ($50-100B+, "WOW")
   - Displays the stark contrast between the two opportunities
6. **Competitive Positioning**: How AxWise compares to competitors
   - **Description:** Explains AxWise's unique market position, focusing on solving a distinct workflow problem for startups rather than competing directly in the traditional QDA market.
   - **Content:** Details the target market (startups/non-researchers), the larger problem addressed (product development waste), market sizing (TAM, SAM, SOM), and Go-to-Market strategy focus (accelerator niches).
   - **Styling:** Clean background, centered text, includes a comparison table (`.competitive-table`).
7. **Team**: Core team members and mentors
8. **Go-to-Market Strategy**: Growth plan
9. **Roadmap**: Phased approach with validation, scale, and category ownership
10. **Vision**: The future AxWise aims to create
11. **The Insight Economy**: The "faster horses" metaphor and AxWise's unique position
12. **Research Insights**: Visualization of key themes and pain points from user research
13. **Target Persona**: Visual representation of our ideal customer
14. **CTA**: Call to action for potential investors

## Files

- `index.html`: Main HTML structure and content
- `style.css`: Styling for all elements
- `main.js`: JavaScript for animations and interactivity
- `img/`: Directory containing SVG icons and team photos
  - `ai.svg`: AI analysis feature icon
  - `ui.svg`: Intuitive UI feature icon
  - `api.svg`: API-First architecture feature icon
  - `persona.svg`: Visual representation of our target user
  - Other team member photos (not yet added)

## Design Elements

### Colors
- Background: Mint green (#e4f7f1) for Solution section and light pink (#f8e5e8) for Problem section
- Accent colors: Purple (#7b68ee) and Pink (#ff6b8b) for highlights and important elements
- Text: Dark text for readability, with accent colors for emphasis

### Layout
- Centered content in all sections with a max-width of 1000px
- Responsive design that adapts to different screen sizes
- Consistent spacing and alignment throughout
- 2-column grid for Problem items and 3-column layout for Features

### Typography

- Main font: 'Inter', sans-serif
- Headings: 2-3.5rem, color `#7b68ee` (purple)
- Body text: 1.1rem, color `#232946` (dark blue)
- Highlights: color `#ff6b8b` (pink)

### Animations

- Fade-in animations for sections as the user scrolls
- Hover effects on cards and buttons
- Animated counters for statistics (with proper display of percentage symbols and x indicators)
- Staggered animations for data points
- Interactive bar charts for research insights

## Data Visualizations

The website now includes several data visualizations based on actual user research:

### Market Transition Visual
- Inline SVG visual showing the transition from the smaller QDA market to the larger product development waste market
- Uses size differential and color-coding (blue for QDA/"MEH" market, pink for product development waste/"WOW" market)
- Includes an arrow connecting the markets to illustrate the strategic transition
- Responsive design that adapts to different screen sizes

### Insight Theme Cards
- Displays the sentiment analysis of key themes from user interviews
- Shows representative quotes from research participants
- Color-coded based on positive/negative sentiment

### Pain Point Bar Chart
- Visual representation of the frequency of different pain points
- Interactive with hover effects
- Shows percentage values for each pain point category

### Solution Mapping
- Maps each identified pain point to AxWise's corresponding solution in a 2x2 grid
- Shows how specific features address key challenges:
  - Guided Interview Framework for teams without UX expertise
  - AI-Powered Intent Analysis for correctly interpreting feedback
  - Automated Dev Task Generation for bridging the insight-to-action gap
  - Automatic Persona Generation for teams that can't create user personas

### Persona Card
- Visual representation of our ideal customer (Pragmatic Product Insights Leader)
- Displays key goals and frustrations
- Includes a representative quote

## Updating the Website

### Modifying Content

To update the content of the website:

1. Edit the `index.html` file to modify text content
2. Maintain the existing structure and section order
3. Keep consistent styling across all sections
4. Ensure any updated numbers or statistics match the latest data

### Updating Research Insights

To update the research insights section:

1. Update the theme cards with new themes, sentiment values, and quotes from research
2. Adjust the bar chart values to reflect updated frequency data
3. Modify the solution mapping to align with AxWise's evolving feature set

### Adding Team Photos

To add team member photos:

1. Place photos in the `img/` directory
2. Use the format `img/name.jpg` as referenced in the HTML
3. Ensure photos are properly sized (recommended: square photos, at least 200x200px)

### Modifying Design

To update the design:

1. Edit the `style.css` file for styling changes
2. Maintain the gradient color scheme and overall visual language
3. Ensure responsive design works on all screen sizes
4. Test any changes across different browsers

## Notes

- All statistics and market data should be updated regularly to reflect current numbers
- The presentation is structured to tell a compelling story about AxWise's unique value proposition
- The "faster horses" metaphor in the Insight Economy section is a key narrative element
- The research insights are based on actual interviews with product managers and UX professionals

## Contact

For questions about the AxWise presentation, please contact Vitalijs Visnevskis.
