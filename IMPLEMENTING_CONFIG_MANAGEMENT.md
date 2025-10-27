# Guide: Implementing Configuration Management in Your React App

This guide provides a step-by-step approach to addressing Recommendation #3 from the audit report: **"Implement Configuration Management."** The goal is to move hardcoded values out of your components and into centralized files, making your application more flexible, maintainable, and easier to translate.

We will tackle this in three parts, from easiest to most complex.

---

## Part 1: Externalizing Application Settings (The Easy Win)

The easiest way to start is by moving simple, non-secret values into a central configuration file. This includes colors, animation timings, default values, and external URLs.

### Concepts to Understand:

*   **Single Source of Truth:** By placing all configuration in one place, you make it easy to update values without hunting through multiple files. If a color needs to change, you change it in one spot.
*   **Separation of Concerns:** Your React components should be responsible for *displaying* the UI, not for *defining* every value it uses. This makes your components cleaner and more reusable.

### Your Implementation Steps:

1.  **Create a Configuration File:**
    *   In your `src/` directory, create a new file named `config.js`.

2.  **Populate the Configuration File:**
    *   Open `config.js` and create an object that will hold your settings.
    *   Find hardcoded values in your code and move them here. Let's use two examples from the audit report:
        *   The `backgroundColor` from `src/atoms.js`.
        *   The DRACO decoder URL from `src/importUtils.jsx`.

    Your `src/config.js` should look something like this:

    ```javascript
    // src/config.js

    const AppConfig = {
      // Visual and Theme settings
      theme: {
        backgroundColor: '#3b3b3b',
        gridColor: '#666666'
        // ...add other colors here
      },

      // Timings and Durations (in milliseconds)
      timeouts: {
        loadingScreen: 3000
      },

      // External URLs and Paths
      urls: {
        dracoDecoder: 'https://www.gstatic.com/draco/versioned/decoders/1.5.7/'
      },

      // Default values
      defaults: {
        downloadFilename: 'animation.webm'
      }
    };

    export default AppConfig;
    ```

3.  **Refactor Your Components to Use the Config File:**
    *   Now, go back to the files where these values were hardcoded and import your new config file.

    **Before (in `src/atoms.js`):**
    ```javascript
    export const backgroundColor = atom('#3b3b3b');
    ```

    **After (in `src/atoms.js`):**
    ```javascript
    import AppConfig from './config';
    export const backgroundColor = atom(AppConfig.theme.backgroundColor);
    ```

    **Before (in `src/importUtils.jsx`):**
    ```javascript
    dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/');
    ```

    **After (in `src/importUtils.jsx`):**
    ```javascript
    import AppConfig from './config';
    dracoLoader.setDecoderPath(AppConfig.urls.dracoDecoder);
    ```

4.  **Continue the Process:**
    *   Repeat this process for all other hardcoded configuration values you can find. This is a safe and easy way to make a big impact on your codebase's quality.

---

## Part 2: Externalizing UI Text (Internationalization - i18n)

Hardcoded text is the biggest barrier to making an application configurable and multi-lingual. The standard solution for this is **Internationalization (i18n)**. We will use a very popular library for this called `react-i18next`.

### Concepts to Understand:

*   **Translation Files:** You will create JSON files that hold your UI text. You'll have at least one file for your default language (e.g., English) and can easily add more for other languages.
*   **Keys:** Instead of writing the text directly in your component, you will use a unique "key" (like a variable name). The i18n library will use this key to look up the correct translation from the appropriate language file.
*   **The `t` function:** `react-i18next` provides a function, conventionally named `t`, that performs this lookup.

### Your Implementation Steps:

1.  **Install the Library:**
    *   You will need to add `react-i18next` and `i18next` to your project.

2.  **Initialize i18next:**
    *   Create a new file, `src/i18n.js`, to configure the library. Here, you will tell it where to find your translation files and what the default language is.

3.  **Create Your First Translation File:**
    *   Create a directory structure like `public/locales/en`.
    *   Inside, create a file named `translation.json`. This is where your English text will go.

    Your `public/locales/en/translation.json` might start like this:

    ```json
    {
      "buttons": {
        "addPerspective": "Add Perspective Camera",
        "addOrthographic": "Add Orthographic Camera"
      },
      "labels": {
        "loading": "Loading..."
      },
      "validation": {
        "mustWriteSomething": "You need to write something!"
      }
    }
    ```

4.  **Refactor a Component:**
    *   Let's refactor `src/addCameraUI.jsx`. You will import the `useTranslation` hook from `react-i18next`, which gives you the `t` function.

    **Before (in `src/addCameraUI.jsx`):**
    ```jsx
    <button>Add Perspective Camera</button>
    <button>Add Orthographic Camera</button>
    ```

    **After (in `src/addCameraUI.jsx`):**
    ```jsx
    import { useTranslation } from 'react-i18next';

    function AddCameraUI() {
      const { t } = useTranslation();

      return (
        <div>
          <button>{t('buttons.addPerspective')}</button>
          <button>{t('buttons.addOrthographic')}</button>
        </div>
      );
    }
    ```

5.  **Continue for All UI Text:**
    *   Go through your application and replace every piece of hardcoded user-facing text with the `t()` function and a corresponding key in your `translation.json` file.

**📚 Essential Reading:**

*   **react-i18next - Step-by-Step Guide:** [This is the official tutorial. Follow it carefully. It's the best resource for getting started.](https://react.i18next.com/latest/getting-started)

---

## Part 3: Externalizing Business Rules

This is the most advanced step. Business rules are the logic in your application that is specific to your domain. The audit found that the camera naming convention is a hardcoded business rule.

### Concepts to Understand:

*   **Decoupling Logic from UI:** Your UI components shouldn't contain complex business logic. When you separate them, you can change the logic without having to rewrite the component, and you can reuse the logic elsewhere.

### Your Implementation Steps:

1.  **Identify the Rule:**
    *   From the audit: The rule for generating a new camera name is `const name = \`Camera${Object.keys(cameras).length + 1}\`;`.

2.  **Move the Rule to a Central Location:**
    *   For simple rules like this, you can add them as functions to your `src/config.js` file. For more complex applications, you might create a dedicated `src/rules.js` file.

    Let's add it to `src/config.js`:

    ```javascript
    // src/config.js

    const AppConfig = {
      // ... all your other config from Part 1 ...

      // Business Rules
      rules: {
        generateCameraName: (cameras) => {
          const count = Object.keys(cameras).length + 1;
          return `Camera${count}`;
        }
      }
    };

    export default AppConfig;
    ```

3.  **Refactor the Component to Use the Rule:**
    *   Now, import the config and call the rule function from your component.

    **Before (in `src/addCameraUI.jsx`):**
    ```javascript
    const name = `Camera${Object.keys(cameras).length + 1}`;
    ```

    **After (in `src/addCameraUI.jsx`):**
    ```javascript
    import AppConfig from './config';
    // ...
    const name = AppConfig.rules.generateCameraName(cameras);
    ```

### Why is this better?

Imagine you later decide that cameras should be named "SceneCamera-01", "SceneCamera-02", etc. With the new approach, you only need to change the `generateCameraName` function in `config.js`. You don't have to touch the React component at all. This makes your code much more robust and easier to maintain.

---

## Conclusion

Start with Part 1. It's the easiest and will help you get comfortable with the pattern of centralizing configuration. Then, move on to Part 2 to handle all the hardcoded text. Finally, tackle the business rules. By the end, your application will be significantly more compliant, maintainable, and professional. Good luck!
