/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './core/**/*.html',
    './core/**/*.js',
    './core/**/*.py', // picks up any class strings in Python if needed
  ],

  theme: {
    screens: {
      xs: '480px',
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
    },

    extend: {
      theme: {
        extend: {
          fontFamily: {
            sans: ['Montserrat', 'Hind Madurai', 'sans-serif'],
            serif: ['Lora', 'serif'],
            ui: ['Hind Madurai', 'sans-serif'],
          },
        },
      },

      colors: {
        // Deep forest green — primary brand, conveys growth and agriculture
        primary: {
          DEFAULT: '#2D5016',
          50: '#f2f7ee',
          100: '#e0ecd4',
          200: '#c1d9a9',
          300: '#a2c67e',
          400: '#83b353',
          500: '#2D5016',
          600: '#274613',
          700: '#203b0f',
          800: '#19300c',
          900: '#122509',
        },

        // Warm amber — secondary, evoking harvest, sunlight, and grain
        secondary: {
          DEFAULT: '#B8860B',
          50: '#fdf8e7',
          100: '#faefc4',
          200: '#f5df89',
          300: '#f0cf4e',
          400: '#ebbf22',
          500: '#B8860B',
          600: '#a07609',
          700: '#876508',
          800: '#6e5406',
          900: '#554304',
        },

        // Terracotta — accent, evokes Nigerian soil and warmth
        accent: {
          DEFAULT: '#C1440E',
          50: '#fdf1ec',
          100: '#fae0d4',
          200: '#f5c1a9',
          300: '#efa17e',
          400: '#ea8253',
          500: '#C1440E',
          600: '#aa3b0c',
          700: '#8f310a',
          800: '#742808',
          900: '#591f06',
        },

        // Off-white with a slight warm tint — light backgrounds
        light: {
          DEFAULT: '#FAF7F2',
          50: '#ffffff',
          100: '#FAF7F2',
          200: '#f3ede4',
          300: '#ece3d6',
          400: '#e5d9c8',
          500: '#decfba',
          600: '#d7c5ac',
          700: '#d0bb9e',
          800: '#c9b190',
          900: '#c2a782',
        },

        // Near-black with a warm undertone — text and dark UI surfaces
        dark: {
          DEFAULT: '#1A1A0F',
          50: '#e8e8e4',
          100: '#d1d1c9',
          200: '#b3b3a8',
          300: '#969687',
          400: '#787866',
          500: '#5a5a45',
          600: '#434332',
          700: '#2d2d1f',
          800: '#22221a',
          900: '#1A1A0F',
        },

        // Semantic surface colours — used for cards, page backgrounds, etc.
        surface: {
          DEFAULT: '#FFFFFF',
          muted: '#F4F1EC',
          border: '#E2DDD6',
        },

        // Semantic status colours
        success: {
          DEFAULT: '#3A7D44',
          light: '#EBF5ED',
        },
        warning: {
          DEFAULT: '#B8860B',
          light: '#FDF6DC',
        },
        danger: {
          DEFAULT: '#C1440E',
          light: '#FDEEE8',
        },
        info: {
          DEFAULT: '#1A5276',
          light: '#EAF2F8',
        },
      },

      borderRadius: {
        'sm': '0.25rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
        '2xl': '1.5rem',
      },

      boxShadow: {
        'card':
          '0 1px 3px 0 rgba(26,26,15,0.08), 0 1px 2px -1px rgba(26,26,15,0.06)',
        'card-md':
          '0 4px 6px -1px rgba(26,26,15,0.08), 0 2px 4px -2px rgba(26,26,15,0.06)',
        'card-lg':
          '0 10px 15px -3px rgba(26,26,15,0.08), 0 4px 6px -4px rgba(26,26,15,0.06)',
      },

      spacing: {
        18: '4.5rem',
        22: '5.5rem',
        72: '18rem',
        84: '21rem',
        96: '24rem',
      },
    },
  },

  plugins: [require('daisyui')],

  daisyui: {
    themes: false, // disable DaisyUI's built-in themes; use your own colours above
    base: false, // do not override your own base styles
    logs: false,
  },
};
