var margin_world = { top: 100, right: 50, bottom: 50, left: 30 },
  width_world = 1100 - margin_world.left - margin_world.right,
  height_world = 550 - margin_world.top - margin_world.bottom;

var xScaleWorld = d3
  .scaleBand()
  .domain([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
  .range([0, width_world])
  .paddingInner(0.05)
  .paddingOuter(0.25);

var yScaleWorld = d3.scaleLinear().domain([0, 828]).range([height_world, 0]);

var xAxisWorld = d3.axisBottom().scale(xScaleWorld);

var yAxisWorld = d3.axisLeft().scale(yScaleWorld);

var svg_world = d3
  .select("#buildings")
  .select("#buildingsBar")
  .append("g")
  .attr(
    "transform",
    "translate(" + margin_world.left + "," + margin_world.top + ")"
  );

// svg_world
//   .append("text")
//   .attr("transform", "translate(" + width_world / 2 + "," + -30 + ")")
//   .style("text-anchor", "middle")
//   .attr("font-family", "Chivo")
//   .attr("font-size", "25px")
//   .attr("font-weight", 300)
//   .text("Complexity of Web Browsing");

d3.csv("resources/buildings.csv", function(data) {
  svg_world
    .selectAll("images")
    .data(
      data.filter(function(d) {
        return +d.rank <= 10;
      })
    )
    .enter()
    .append("svg:image")
    .attr("class", "images")
    .attr("x", function(d) {
      return xScaleWorld(+d.rank);
    })
    .attr("y", function(d) {
      return yScaleWorld(d.height);
    })
    .attr("width", 100)
    .attr("height", function(d) {
      return height_world - yScaleWorld(d.height);
    })
    .attr("xlink:href", function(d) {
      return "resources/images/" + d.link;
    })
    .on("mouseover", function(d) {
      var xPosition_world =
        parseFloat(d3.select(this).attr("x")) + xScaleWorld.bandwidth() / 2;

      svg_world
        .append("text")
        .attr("class", "tooltipWorld")
        .attr("x", xPosition_world)
        .attr("y", yScaleWorld(d.height) - 50)
        .attr("text-anchor", "middle")
        .style("font-size", "11px")
        .style("font-weight", "400")
        .style("font-family", "Chivo")
        .style("text-decoration", "underline")
        .text(d.name);

      svg_world
        .append("text")
        .attr("class", "tooltipWorld")
        .attr("x", xPosition_world)
        .attr("y", yScaleWorld(d.height) - 20)
        .attr("text-anchor", "middle")
        .style("font-size", "10px")
        .style("font-weight", "300")
        .style("font-family", "Chivo")
        .text("Height: " + d.height + " m");

      svg_world
        .append("text")
        .attr("class", "tooltipWorld")
        .attr("x", xPosition_world)
        .attr("y", yScaleWorld(d.height) - 35)
        .attr("text-anchor", "middle")
        .style("font-size", "10px")
        .style("font-weight", "300")
        .style("font-family", "Chivo")
        .text(d.city + ", " + d.country);
    })
    .on("mouseout", function(_) {
      svg_world.selectAll(".tooltipWorld").remove();
    });
});
