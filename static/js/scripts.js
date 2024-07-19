// // Login form submission
// document
//   .getElementById("login-form")
//   .addEventListener("submit", function (event) {
//     event.preventDefault();

//     const formData = new FormData(event.target);
//     const data = Object.fromEntries(formData.entries());

//     fetch("/auth/login", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify(data),
//     })
//       .then((response) => response.json())
//       .then((data) => {
//         if (data.access_token) {
//           localStorage.setItem("jwt_token", data.access_token);
//           window.location.href = "/dashboard"; // Redirect to dashboard
//         } else {
//           alert("Login failed");
//         }
//       })
//       .catch((error) => console.error("Error:", error));
//   });

// Login form submission
document
  .getElementById("login-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    fetch("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.access_token) {
          localStorage.setItem("jwt_token", data.access_token);
          window.location.href = "/dashboard"; // Redirect to dashboard
        } else {
          alert("Login failed");
        }
      })
      .catch((error) => console.error("Error:", error));
  });

// Logout functionality
document.getElementById("logout-button").addEventListener("click", function () {
  fetch("/auth/logout")
    .then(() => {
      localStorage.removeItem("jwt_token");
      window.location.href = "/";
    })
    .catch((error) => console.error("Error:", error));
});

// Additional scripts for UI enhancements
// Example: Toggle navigation menu
document.getElementById("menu-toggle").addEventListener("click", function () {
  document.getElementById("navbar").classList.toggle("open");
});
