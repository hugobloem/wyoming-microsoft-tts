# Changelog

## [1.2.0](https://github.com/hugobloem/wyoming-microsoft-tts/compare/v1.1.2...v1.2.0) (2025-02-23)


### 🚀 Features

* support multilingual voices from the secondaryLocaleList ([#99](https://github.com/hugobloem/wyoming-microsoft-tts/issues/99)) ([876c4a5](https://github.com/hugobloem/wyoming-microsoft-tts/commit/876c4a53e4b9f886b84175b83980ad8e3d42ba25))


### 🧪 Tests

* add python 3.13 ([#100](https://github.com/hugobloem/wyoming-microsoft-tts/issues/100)) ([079a1fa](https://github.com/hugobloem/wyoming-microsoft-tts/commit/079a1fa7045218b458d9c6886dc0968abdedb833))

## [1.1.2](https://github.com/hugobloem/wyoming-microsoft-tts/compare/v1.1.1...v1.1.2) (2025-01-29)


### 🏗️ Maintenance

* **deps:** bump azure-cognitiveservices-speech from 1.41.1 to 1.42.0 ([#94](https://github.com/hugobloem/wyoming-microsoft-tts/issues/94)) ([f70c126](https://github.com/hugobloem/wyoming-microsoft-tts/commit/f70c1261c20eb4b689b23a8110112fd1ce10b1c0))
* **deps:** update black requirement from &lt;25,&gt;=24 to >=24,<26 ([#96](https://github.com/hugobloem/wyoming-microsoft-tts/issues/96)) ([051a3fc](https://github.com/hugobloem/wyoming-microsoft-tts/commit/051a3fc9d425af302bb72882e96f9493be4a3526))

## [1.1.1](https://github.com/hugobloem/wyoming-microsoft-tts/compare/v1.1.0...v1.1.1) (2024-11-23)


### 🐛 Bugfixes

* use name of synthesize voice ([#89](https://github.com/hugobloem/wyoming-microsoft-tts/issues/89)) ([3f4a1f8](https://github.com/hugobloem/wyoming-microsoft-tts/commit/3f4a1f854c8048168cce7489547a0846052bce38))

## [1.1.0](https://github.com/hugobloem/wyoming-microsoft-tts/compare/1.0.8...v1.1.0) (2024-11-23)


### 🚀 Features

* add signal handling for graceful shutdown in main execution ([a63a1f4](https://github.com/hugobloem/wyoming-microsoft-tts/commit/a63a1f483395ce3fee8f77b72056041791b347da))
* enhance argument parsing and validation with environment variable support ([a63a1f4](https://github.com/hugobloem/wyoming-microsoft-tts/commit/a63a1f483395ce3fee8f77b72056041791b347da))


### 🐛 Bugfixes

* add exit call for graceful shutdown on stop signal ([#88](https://github.com/hugobloem/wyoming-microsoft-tts/issues/88)) ([b99f441](https://github.com/hugobloem/wyoming-microsoft-tts/commit/b99f441349b3146757c8aeef51d7fa2659963a29))
* add-on button url ([#77](https://github.com/hugobloem/wyoming-microsoft-tts/issues/77)) ([3532cee](https://github.com/hugobloem/wyoming-microsoft-tts/commit/3532ceedf16a5b91898a9c07abc32ea9de6132a3))
* validate and use default voice in event handling ([#82](https://github.com/hugobloem/wyoming-microsoft-tts/issues/82)) ([320a226](https://github.com/hugobloem/wyoming-microsoft-tts/commit/320a226d6be4cae3f758c0d18458579c99a47024))


### 🔨 Code Refactoring

* enhance error handling and logging in voice loading and synthesis processes ([#87](https://github.com/hugobloem/wyoming-microsoft-tts/issues/87)) ([363a46a](https://github.com/hugobloem/wyoming-microsoft-tts/commit/363a46ad35fa4227c5079c794f58e60960458355))


### 👷 Continuous Integration

* add release-please configuration and workflow files ([#83](https://github.com/hugobloem/wyoming-microsoft-tts/issues/83)) ([dd370fc](https://github.com/hugobloem/wyoming-microsoft-tts/commit/dd370fc33df27d7560be11974661201be04fb32e))
* add required packages ([#76](https://github.com/hugobloem/wyoming-microsoft-tts/issues/76)) ([5e89262](https://github.com/hugobloem/wyoming-microsoft-tts/commit/5e8926288fc36055ddf5640181f38ebd940396af))
* enhance Docker image tagging and labeling in release workflow ([#85](https://github.com/hugobloem/wyoming-microsoft-tts/issues/85)) ([88ff459](https://github.com/hugobloem/wyoming-microsoft-tts/commit/88ff459be2818dbeb421c7c905b4ebc4fa1cee3b))
