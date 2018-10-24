/* eslint-disable react/prefer-stateless-function */
// import React, { Component } from "react"
// import { Route } from "react-router-dom"

// import {connect} from 'react-redux';

// import Map from './components/Map';
// import EstuariesList from './components/EstuariesList';
// import EstuaryDetails from './components/EstuaryDetails';
// import FiltersList from './components/FiltersList';
// import NavBar from './components/NavBar';
// import Footer from './components/Footer';
// import Header from "./components/Header"
// import Home from "./components/Home"
// import {
//     setActiveTab,
//     setSearchText,
//     setSearchSort,
//     setSelectedID,
//     setBounds,
//     setFilter,
//     resetFilters,
//     toggleFilterClosed
// } from './modules';
// import {fullBounds} from "./constants";
// import './core.css';

// class App extends Component {
// constructor(props) {
//     super(props);

//     const {dimensionCounts, bounds, history} = this.props;

//     this.state = {
//         view: history.location.pathname.split('/')[1]
//     };

//     history.listen((location) => {
//         ReactGA.set({page: location.pathname})
//         ReactGA.pageview(location.pathname);

//         const view = location.pathname.split('/')[1];

//         // make sure to always show the first view of the selected target (compare or explore)
//         if (this.props.activeTab === 'map') {
//             this.props.setActiveTab(view);
//         }

//         // Ignore details view as a change
//         if (view !== 'details' && view !== this.state.view) {
//             // this isn't working properly to clear out selected ID

//             // if switching between home, compare, explore views, reset all filters except bounds filter
//             // console.log('on route change', view)

//             this.props.setSearchText('');
//             this.props.resetFilters();

//             if (view === '') {
//                 // home, resets bounds to initial
//                 this.props.setBounds(fullBounds);
//             }

//             if (this.props.selectedID !== null) {
//                 this.props.setSelectedID(null);
//             }

//             this.setState({view});
//         }
//     });

//     this._boundsHistory = [bounds];

//     this._dimensionRanges = {};
//     Object.keys(dimensionCounts).forEach(k => {
//         // max value plus 20%
//         this._dimensionRanges[k] = Math.ceil(1.2 * Math.max(...Object.values(dimensionCounts.type)));
//     });

//     // rehydrate selectedID from path on startup.
//     const pathParts = props.location.pathname.split('/');
//     if (pathParts.length === 3 && pathParts[2].length > 0) {
//         const selectedID = parseInt(pathParts[2], 10);
//         if (selectedID !== props.selectedID) {
//             props.setSelectedID(selectedID);
//         }
//     }
// }

// handleBoundsChange = (bounds) => {
//     this.props.setBounds(bounds);

//     // only add bounds to the history if we are not looking at a selected item, this allows us to go back to prev
//     // extent when unselecting that item (below)
//     if (this.props.selectedID === null) {
//         this._boundsHistory.push(bounds);
//     }
// }

// handleBack = () => {
//     // Go back to the previous extent before selecting the item
//     if (this._boundsHistory.length > 0) {
//         const prevBounds = this._boundsHistory.pop();
//         console.log('prev bounds', prevBounds)
//         this.handleBoundsChange(prevBounds);
//     }

//     const next = (this.state.view === 'compare') ? '/compare' : '/explore';
//     this.props.history.push(next);

//     this.props.setSelectedID(null); // clear the selection
// }

// handleZoomClick = () => {
//     console.log('selected ID', this.props.selectedID, window.index[this.props.selectedID].bounds)
//     if (this.props.selectedID === null) return;
//     this.props.setBounds(window.index[this.props.selectedID].bounds);
//     this.props.setActiveTab('map');
// }

// renderMapView() {
//     // for all views except Home
//     const {
//         activeTab, setActiveTab,
//         data, selectedID, setSelectedID,  // general
//         bounds, basemap,  // map props
//         searchText, sort, setSearchText, setSearchSort,  // list props
//         filters, dimensionCounts, closedFilters, setFilter, toggleFilterClosed  // filter props

//     } = this.props;

//     return (
//         <div className="full-height no-overflow">
//             <div className="columns is-gapless full-height">
//                 <div className={"column is-3 sidebar overflow-y no-overflow-x" + ((activeTab !== 'map')? ' full-height': '')}>
//                     <div className="is-hidden-tablet tabs is-boxed is-fullwidth">
//                         <ul>
//                             <Route path='/explore' exact render={() => (
//                                 <li className={(activeTab !== 'map')? 'is-active' : null} onClick={() => setActiveTab('explore')}>
//                                     <a>Explore</a>
//                                 </li>
//                             )}/>

//                             <Route path='/compare' exact render={() => (
//                                 <li className={(activeTab !== 'map')? 'is-active' : null} onClick={() => setActiveTab('compare')}>
//                                     <a>Compare</a>
//                                 </li>
//                             )}/>

//                             <Route path='/details' render={() => (
//                                 <li className={(activeTab !== 'map')? 'is-active' : null} onClick={() => setActiveTab('details')}>
//                                     <a>Details</a>
//                                 </li>
//                             )}/>

//                             <li className={activeTab === 'map' ? 'is-active' : null} onClick={() => setActiveTab('map')}>
//                                 <a>Map</a>
//                             </li>
//                         </ul>
//                     </div>

//                     <div className={(activeTab === 'map')? 'is-hidden-mobile': 'full-height'}>

//                         <Route path='/explore' exact render={() => <EstuariesList
//                             data={data}
//                             searchText={searchText}
//                             sort={sort}
//                             onSearchChange={setSearchText}
//                             onSortChange={setSearchSort}
//                             onSelectID={setSelectedID}/>}/>

//                         <Route path='/details/:id' render={({match}) => <EstuaryDetails
//                             onBack={this.handleBack}
//                             onZoomClick={this.handleZoomClick} {...window.index[match.params.id]} />}/>

//                         <Route path='/compare' exact render={() => <FiltersList
//                             filters={filters}
//                             counts={dimensionCounts}
//                             ranges={this._dimensionRanges}
//                             closedFilters={closedFilters}
//                             onFilterChange={setFilter}
//                             toggleFilterClosed={toggleFilterClosed}/>}/>
//                     </div>
//                 </div>

//                 <div className={"column map" }>
//                     <Map data={data}
//                          bounds={bounds}
//                          basemap={basemap}
//                          selectedID={selectedID}
//                          view={this.state.view}
//                          onSelectID={setSelectedID}
//                          onBoundsChange={this.handleBoundsChange}/>
//                 </div>
//             </div>
//         </div>
//     );
// }

//     render() {
//         return (
//             <div className="flex-column full-height">
//                 <Header />
//                 <div className="main">
//                     <Route exact path="/" component={Home} />
//                     {/* <Route path='/:anything' render={() => this.renderMapView()}/> */}
//                 </div>
//                 {/* <Footer/> */}
//             </div>
//         )
//     }
// }

// const mapStateToProps = state => {
//     return {
//         activeTab: state.activeTab,
//         searchText: state.searchText,
//         sort: state.sort,
//         data: state.data,
//         bounds: state.bounds,
//         basemap: state.basemap,
//         selectedID: state.id,
//         filters: state.filters,
//         dimensionCounts: state.dimensionCounts,
//         closedFilters: state.closedFilters
//     }
// };

// export default withRouter(connect(mapStateToProps, {
//     setActiveTab,
//     setBounds,
//     setSearchText,
//     setSearchSort,
//     setSelectedID,
//     setFilter,
//     resetFilters,
//     toggleFilterClosed
// })(App));

// export default App

// Map related stuff

// TODO: things cut out of above

// static getDerivedStateFromProps(nextProps) {
//     const {
//         location, drawingGeometry, footprint, zoi
//     } = nextProps
//     return {
//         location: fromJS(location),
//     }
// }

// componentDidUpdate(prevProps, prevState) {
//     // console.log('componentDidUpdate', prevState, this.state)
//     // Use this function to update the state of the map object to the current state
//     // of this component

//     const {
//         location, drawingGeometry, footprint, zoi
//     } = this.state
//     const {
//         location: prevLocation,
//         drawingGeometry: prevDrawingGeometry,
//         footprint: prevFootprint,
//         zoi: prevZOI
//     } = prevState

//     // Update the location marker if needed or remove it
//     if (!is(location, prevLocation)) {
//         this.setLocationMarker()
//     }

//     // Update drawing geometry
//     if (!is(drawingGeometry, prevDrawingGeometry)) {
//         this.setDrawingGeometry()
//     }
// }

// TODO: enable this if we want animated markers
// const addAnimatedLocationToMap = (map, { latitude, longitude }) => {
//     map.addSource('location', {
//         type: 'geojson',
//         data: {
//             type: 'Point',
//             coordinates: [longitude, latitude]
//         }
//     })
//     locationStyle.forEach(style => map.addLayer(style))

//     // setup animation
//     const framesPerSecond = 15
//     const { 'circle-opacity': initialOpacity, 'circle-radius': initialRadius } = locationStyle[0].paint
//     const maxRadius = 15

//     let radius = initialRadius
//     let opacity = initialOpacity
//     let counter = 0
//     // derived from: https://bl.ocks.org/danswick/2f72bc392b65e77f6a9c
//     const animateMarker = () => {
//         // TODO: store this timeout someplace so we can kill it later
//         setTimeout(() => {
//             requestAnimationFrame(animateMarker)
//             counter++

//             radius += (maxRadius - radius) / framesPerSecond
//             opacity -= 0.9 / framesPerSecond
//             opacity = Math.max(opacity, 0)

//             map.setPaintProperty('location-point1', 'circle-radius', radius)
//             map.setPaintProperty('location-point1', 'circle-opacity', opacity)

//             // if (opacity <= 0) {
//             if (counter >= framesPerSecond) {
//                 counter = 0
//                 radius = initialRadius
//                 opacity = initialOpacity
//             }
//         }, 1000 / framesPerSecond)
//     }
//     animateMarker()
// }

// setLocationMarker = () => {
//     const { location } = this.state

//     if (location !== null) {
//         const { latitude, longitude } = location.toObject()
//         this.map.flyTo({ center: [longitude, latitude], zoom: 10 })

//         if (!this.locationMarker) {
//             this.locationMarker = new mapboxgl.Marker().setLngLat([longitude, latitude]).addTo(this.map)
//         } else {
//             this.locationMarker.setLngLat([longitude, latitude])
//         }
//     } else {
//         this.locationMarker.remove()
//         this.locationMarker = null
//     }
// }

// addLayerToMap = (layer) => {
//     // TODO: caller is responsible for setting next available color from palette if no
//     // color is defined for dataset (requires state management in container)
//     const { overlayStyle, minZoom, maxZoom } = layer
//     const source = `layer-${layer.datasetId}`
//     const options = {
//         type: 'vector',
//         tiles: [`${window.location.protocol}//${TILESERVER_HOST}/services/${layer.datasetId}/tiles/{z}/{x}/{y}.pbf`]
//     }
//     if (minZoom) {
//         options.minzoom = minZoom
//     }
//     if (maxZoom) {
//         options.maxzoom = maxZoom
//     }
//     this.map.addSource(source, options)

//     console.log('adding layer', layer, `/services/${layer.datasetId}/tiles/{z}/{x}/{y}.pbf`)

//     overlayStyle.forEach((style, i) => {
//         this.map.addLayer(
//             Object.assign(
//                 {
//                     id: `${source}-${i}`,
//                     source,
//                     'source-layer': 'data', // 'data' is hard-coded into vector tile creation pipeline
//                     layout: {
//                         visibility: !layer.hidden ? 'visible' : 'none'
//                     }
//                 },
//                 style
//             )
//         )
//     })
// }

// const colors = ["Texas", "#FF0000", "North Carolina", "#00FF00", "#FFF"]
// map.addLayer({
//     id: "states-fill",
//     source: "states",
//     "source-layer": "states",
//     type: "fill",
//     layout: {}, // TODO: set as not visible by default
//     paint: {
//         "fill-opacity": 0.6,
//         "fill-color": [
//             "match",
//             ["get", "NAME"],
//             ...colors
//         ]
//     }
// })
