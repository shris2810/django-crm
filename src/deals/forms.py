from django import forms
from .models import Deal


class DealStageForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ["stage", "lost_reason"]

    def clean(self):
        cleaned_data = super().clean()
        stage = cleaned_data.get("stage")
        lost_reason = cleaned_data.get("lost_reason")

        # Require a lost_reason if the stage is LOST
        if stage == Deal.Stage.LOST and not lost_reason:
            self.add_error(
                "lost_reason", "A lost reason is required when marking a deal as Lost."
            )

        # Clear the lost reason if the stage is not LOST
        if stage != Deal.Stage.LOST and lost_reason:
            cleaned_data["lost_reason"] = None

        return cleaned_data
