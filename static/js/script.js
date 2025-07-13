document.addEventListener('DOMContentLoaded', function () {
    const voteButton = document.getElementById('vote-button');
    if (voteButton) {
        voteButton.addEventListener('click', function () {
            voteButton.disabled = true;
            voteButton.textContent = 'Submitting...';
        });
    }
});
function confirmVote(candidateName) {
    return confirm(`Are you sure you want to vote for ${candidateName}?`);
}
setInterval(function () {
    const now = new Date();
    document.getElementById("clock").textContent = now.toLocaleTimeString();
}, 1000);
