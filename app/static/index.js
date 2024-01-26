const dropdownItems = document.querySelectorAll('.state-item');

// Add click event listener to each item
dropdownItems.forEach(item => {
  item.addEventListener('click', function() {
    // Update button text with selected state
    document.getElementById('dropdownMenuButton').innerText = this.innerText;
  });
});


