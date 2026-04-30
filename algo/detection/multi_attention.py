# 伪代码示意
class CrossModalAttention:
    def forward(self, text_feat, image_feat):
        # Q来自文本，K、V来自图像
        attention_scores = softmax(Q_text @ K_image.T / sqrt(d))
        fused_feat = attention_scores @ V_image
        return fused_feat + text_feat  # 残差连接