from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from voting.models import Vote, VoteOption, VoteAnswer
from voting.forms import VoteCreateForm, VoteForm

User = get_user_model()

class VotingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(
            username="creator@example.com",
            password="pass"
        )
        self.voter = User.objects.create_user(
            username="voter@example.com",
            password="pass"
        )

        self.vote = Vote.objects.create(
            creator=self.creator,
            title="Test Vote",
            level=Vote.Level.SCHOOL,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
            multiple_choices_allowed=False,
        )
        self.option1 = VoteOption.objects.create(vote=self.vote, text="Option 1")
        self.option2 = VoteOption.objects.create(vote=self.vote, text="Option 2")


    def test_vote_list_authenticated(self):
        self.client.login(username="voter", password="pass")
        res = self.client.get(reverse("vote_list"))
        self.assertEqual(res.status_code, 200)

    def test_vote_detail_and_submit(self):
        self.client.login(username="voter", password="pass")
        res = self.client.post(reverse("vote_detail", args=[self.vote.id]), {
            "options": str(self.option1.id)
        })
        self.assertRedirects(res, reverse("vote_detail", args=[self.vote.id]))
        self.assertTrue(VoteAnswer.objects.filter(voter=self.voter, option=self.option1).exists())

    def test_vote_create_form_invalid_dates(self):
        form = VoteCreateForm(data={
            "title": "Bad Vote",
            "level": Vote.Level.SCHOOL,
            "start_date": timezone.now() + timedelta(days=1),
            "end_date": timezone.now()
        })
        self.assertFalse(form.is_valid())
        self.assertIn("Дата початку повинна бути раніше дати завершення.", form.errors["__all__"])

    def test_vote_form_field_type(self):
        form = VoteForm(self.vote)
        self.assertIn("options", form.fields)
        self.assertEqual(form.fields["options"].widget.__class__.__name__, "RadioSelect")
