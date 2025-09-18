import React, { useState } from "react";
import { Palette, Type, Eye, Settings } from "lucide-react";

const StyleOptions = ({ styles, availableStyles, onChange }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleChange = (key, value) => {
    onChange({
      ...styles,
      [key]: value,
    });
  };

  if (!availableStyles) return null;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Palette className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">
            🎨 Subtitle Styling
          </h2>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
        >
          <Settings className="h-4 w-4" />
          <span>{isExpanded ? "Hide Options" : "Show Options"}</span>
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-6">
          {/* Display Mode */}
          <div>
            <label className="label">
              <Eye className="h-4 w-4 inline mr-2" />
              Display Mode
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="word_mode"
                  checked={styles.word_mode}
                  onChange={() => handleChange("word_mode", true)}
                  className="text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">
                  Word-by-word (with highlighting)
                </span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="word_mode"
                  checked={!styles.word_mode}
                  onChange={() => handleChange("word_mode", false)}
                  className="text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">
                  Line-by-line (traditional)
                </span>
              </label>
            </div>
          </div>

          {/* Font Settings */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="label">
                <Type className="h-4 w-4 inline mr-2" />
                Font Size
              </label>
              <div className="space-y-2">
                <input
                  type="range"
                  min="16"
                  max="48"
                  value={styles.font_size}
                  onChange={(e) =>
                    handleChange("font_size", parseInt(e.target.value))
                  }
                  className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
                  <span>16px</span>
                  <span className="font-semibold text-primary-600 dark:text-primary-400">
                    {styles.font_size}px
                  </span>
                  <span>48px</span>
                </div>
              </div>
            </div>

            <div>
              <label className="label">Font Family</label>
              <input
                type="text"
                value={styles.font_family}
                onChange={(e) => handleChange("font_family", e.target.value)}
                placeholder="Arial-Bold or /path/to/font.ttf"
                className="input-field"
              />
            </div>
          </div>

          {/* Colors */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="label">Font Color</label>
              <div className="grid grid-cols-4 gap-2">
                {availableStyles.font_colors.map((color) => (
                  <button
                    key={color}
                    onClick={() => handleChange("font_color", color)}
                    className={`
                      px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
                      ${
                        styles.font_color === color
                          ? "ring-2 ring-primary-500 bg-primary-100 dark:bg-primary-900 text-primary-900 dark:text-primary-100"
                          : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                      }
                    `}
                    style={{
                      backgroundColor:
                        color === "white"
                          ? "#ffffff"
                          : color === "black"
                          ? "#000000"
                          : color,
                    }}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="label">Highlight Color</label>
              <div className="grid grid-cols-4 gap-2">
                {availableStyles.highlight_colors.map((color) => (
                  <button
                    key={color}
                    onClick={() => handleChange("highlight_color", color)}
                    className={`
                      px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
                      ${
                        styles.highlight_color === color
                          ? "ring-2 ring-primary-500 bg-primary-100 dark:bg-primary-900 text-primary-900 dark:text-primary-100"
                          : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                      }
                    `}
                    style={{
                      backgroundColor:
                        color === "white"
                          ? "#ffffff"
                          : color === "black"
                          ? "#000000"
                          : color,
                    }}
                  >
                    {color}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Padding */}
          <div>
            <label className="label">Bottom Padding</label>
            <div className="space-y-2">
              <input
                type="range"
                min={availableStyles.bottom_padding_range.min}
                max={availableStyles.bottom_padding_range.max}
                value={styles.bottom_padding}
                onChange={(e) =>
                  handleChange("bottom_padding", parseInt(e.target.value))
                }
                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>{availableStyles.bottom_padding_range.min}px</span>
                <span className="font-semibold text-primary-600 dark:text-primary-400">
                  {styles.bottom_padding}px
                </span>
                <span>{availableStyles.bottom_padding_range.max}px</span>
              </div>
            </div>
          </div>

          {/* Preview */}
          <div className="p-4 bg-slate-900 rounded-lg">
            <p className="text-sm text-slate-400 mb-2">Preview:</p>
            <div
              className="text-center"
              style={{
                fontSize: `${styles.font_size}px`,
                color: styles.font_color,
                fontFamily: styles.font_family,
                paddingBottom: `${styles.bottom_padding}px`,
              }}
            >
              <span>This is how your subtitles will look</span>
              {styles.word_mode && (
                <span
                  className="ml-2"
                  style={{ color: styles.highlight_color }}
                >
                  with highlighting
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StyleOptions;
