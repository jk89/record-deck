import numpy as np

def get_sin_model(poles):
    sin_period_coeff = (poles / 2)
    def sin_model(angular_position, angular_displacement_cw, phase_current_displacement_cw):
        coefficient=1.0
        phase_a_current = np.zeros((1,angular_position.shape[0]))# 0
        phase_b_current = np.zeros((1,angular_position.shape[0]))# 0
        phase_c_current = np.zeros((1,angular_position.shape[0])) # 0
        phase_a_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement_cw))
        phase_b_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement_cw + phase_current_displacement_cw))
        phase_c_current += coefficient * np.sin(sin_period_coeff * (angular_position + angular_displacement_cw + (2 * phase_current_displacement_cw)))
        return np.asarray([phase_a_current, phase_b_current, phase_c_current]).ravel()
    return sin_model
