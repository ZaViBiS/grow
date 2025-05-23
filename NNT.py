import math
import random


class SimpleNNTemperatureController:
    def __init__(
        self,
        target_temp=25.0,
        learning_rate=0.3,
        momentum=0.8,
        scale_factor_temp_diff_input=5.0,
        scale_factor_error_gradient=5.0,
    ):
        self.target_temp = target_temp
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.scale_factor_temp_diff_input = scale_factor_temp_diff_input
        self.scale_factor_error_gradient = scale_factor_error_gradient

        self.weight_temp_diff = random.uniform(0.1, 0.3)
        self.weight_prev_fan_speed = random.uniform(-0.05, 0.05)
        self.bias = random.uniform(0.0, 0.1)

        self.prev_delta_weight_temp_diff = 0.0
        self.prev_delta_weight_prev_fan_speed = 0.0
        self.prev_delta_bias = 0.0

        self.prev_fan_speed_0_to_1 = 0.0

        # --- Параметри симуляції оточення (використовуються тільки в тестовому блоці `if __name__ == "__main__":`) ---
        self.AMBIENT_TEMP = 35.0
        self.THERMAL_INERTIA = 0.08
        self._current_temp_simulated = 30.0  # Внутрішня змінна для симуляції

    def _tanh_scaled(self, x):
        return (math.tanh(x) + 1) / 2

    def _tanh_scaled_derivative(self, y):
        deriv = 0.5 * (1 - (2 * y - 1) ** 2)
        return max(deriv, 0.02)

    # --- Функції симуляції (для тестування на ПК) ---
    def _get_current_temperature_simulated(self, fan_speed_0_to_1):
        """
        Симуляція читання температури для ПК.
        Імітує зміну температури в залежності від швидкості вентилятора.
        """
        # Зміна _current_temp_simulated відбувається тут
        cooling_power = fan_speed_0_to_1 * 15
        effective_ambient_temp = self.AMBIENT_TEMP - cooling_power
        temp_change = (
            effective_ambient_temp - self._current_temp_simulated
        ) * self.THERMAL_INERTIA

        self._current_temp_simulated += temp_change
        self._current_temp_simulated += random.uniform(-0.05, 0.05)  # Додаємо шум

        self._current_temp_simulated = max(
            15.0, min(45.0, self._current_temp_simulated)
        )
        return self._current_temp_simulated

    def predict_fan_speed(self, current_temp):
        input_temp_diff = (
            current_temp - self.target_temp
        ) / self.scale_factor_temp_diff_input
        input_prev_fan_speed = self.prev_fan_speed_0_to_1

        weighted_sum = (
            (self.weight_temp_diff * input_temp_diff)
            + (self.weight_prev_fan_speed * input_prev_fan_speed)
            + self.bias
        )

        new_fan_speed_0_to_1 = self._tanh_scaled(weighted_sum)
        new_fan_speed_0_to_1 = max(0.0, min(1.0, new_fan_speed_0_to_1))

        self.prev_fan_speed_0_to_1 = new_fan_speed_0_to_1

        new_fan_speed_0_to_100 = round(new_fan_speed_0_to_1 * 100)
        new_fan_speed_0_to_100 = int(max(0, min(100, new_fan_speed_0_to_100)))

        return new_fan_speed_0_to_100

    def learn(self, temp_before_action, temp_after_action, fan_speed_applied_0_to_100):
        fan_speed_applied_0_to_1 = fan_speed_applied_0_to_100 / 100.0

        input_temp_diff_for_learning = (
            temp_before_action - self.target_temp
        ) / self.scale_factor_temp_diff_input
        input_prev_fan_speed_for_learning = fan_speed_applied_0_to_1

        weighted_sum_for_learning = (
            (self.weight_temp_diff * input_temp_diff_for_learning)
            + (self.weight_prev_fan_speed * input_prev_fan_speed_for_learning)
            + self.bias
        )

        predicted_output_0_to_1 = self._tanh_scaled(weighted_sum_for_learning)
        predicted_output_0_to_1 = max(0.0, min(1.0, predicted_output_0_to_1))

        error_signal = temp_after_action - self.target_temp
        scaled_error_signal = error_signal / self.scale_factor_error_gradient

        delta_output = scaled_error_signal * self._tanh_scaled_derivative(
            predicted_output_0_to_1
        )

        delta_weight_temp_diff = (
            self.learning_rate * delta_output * input_temp_diff_for_learning
        )
        delta_weight_prev_fan_speed = (
            self.learning_rate * delta_output * input_prev_fan_speed_for_learning
        )
        delta_bias = self.learning_rate * delta_output

        self.weight_temp_diff += (
            delta_weight_temp_diff + self.momentum * self.prev_delta_weight_temp_diff
        )
        self.weight_prev_fan_speed += (
            delta_weight_prev_fan_speed
            + self.momentum * self.prev_delta_weight_prev_fan_speed
        )
        self.bias += delta_bias + self.momentum * self.prev_delta_bias

        self.prev_delta_weight_temp_diff = delta_weight_temp_diff
        self.prev_delta_weight_prev_fan_speed = delta_weight_prev_fan_speed
        self.prev_delta_bias = delta_bias

    def get_weights(self):
        return {
            "w_temp_diff": self.weight_temp_diff,
            "w_prev_fan_speed": self.weight_prev_fan_speed,
            "bias": self.bias,
        }


# --- Приклад використання класу на ПК (симуляція) ---
if __name__ == "__main__":
    controller = SimpleNNTemperatureController(
        target_temp=25.0,
        learning_rate=0.3,
        momentum=0.8,
        scale_factor_temp_diff_input=5.0,
        scale_factor_error_gradient=5.0,
    )

    print("Запуск симуляції контролера температури NN (з розділеною логікою).")
    print(f"Цільова температура: {controller.target_temp}°C")
    # Ініціалізуємо симульовану температуру для тестування
    current_simulated_temp = (
        controller._current_temp_simulated
    )  # Беремо початкове значення з контролера

    try:
        for iteration in range(2000):
            # --- Етап 1: Передбачення (вимірюємо і розраховуємо) ---
            temp_before_action = (
                current_simulated_temp  # Використовуємо поточну симульовану температуру
            )

            # Нейромережа розраховує швидкість
            fan_speed_to_apply = controller.predict_fan_speed(temp_before_action)

            # --- Етап 2: Дія та очікування (вентилятор працює, температура змінюється) ---
            # ЦЕ ТЕ МІСЦЕ, ДЕ РАНІШЕ БУЛА ПЛУТАНИНА.
            # Тепер ми ЯВНО викликаємо функцію симуляції, щоб оновити температуру.
            # Ця функція _get_current_temperature_simulated оновлює внутрішню змінну _current_temp_simulated
            # та повертає її, тому ми присвоюємо її нашій локальній current_simulated_temp.
            current_simulated_temp = controller._get_current_temperature_simulated(
                fan_speed_to_apply / 100.0
            )

            # time.sleep(0.5) # У реальному ESP32 тут буде затримка (наприклад, 10 секунд)

            # --- Етап 3: Навчання (знову вимірюємо та повідомляємо нейромережі результат) ---
            temp_after_action = (
                current_simulated_temp  # Це температура після впливу вентилятора
            )

            # Нейромережа навчається
            controller.learn(temp_before_action, temp_after_action, fan_speed_to_apply)

            # --- Виведення для відладки ---
            print(f"\n--- Ітерація {iteration + 1} ---")
            print(
                f"Темп до дії: {temp_before_action:.2f}°C, Темп після дії: {temp_after_action:.2f}°C"
            )
            print(
                f"Ціль: {controller.target_temp}°C, Помилка: {temp_after_action - controller.target_temp:.2f}°C"
            )
            print(
                f"Розрахована/Застосована швидкість вентилятора: {fan_speed_to_apply}%"
            )
            weights = controller.get_weights()
            print(
                f"Ваги: w_temp_diff={weights['w_temp_diff']:.4f}, "
                f"w_prev_fan_speed={weights['w_prev_fan_speed']:.4f}, "
                f"bias={weights['bias']:.4f}"
            )

    except KeyboardInterrupt:
        print("\nЗупинка симуляції.")
