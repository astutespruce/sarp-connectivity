/* eslint-disable react/prefer-stateless-function */
import React, { Component } from "react"
import { Route } from "react-router-dom"


// import {connect} from 'react-redux';

// import Map from './components/Map';
// import EstuariesList from './components/EstuariesList';
// import EstuaryDetails from './components/EstuaryDetails';
// import FiltersList from './components/FiltersList';
// import NavBar from './components/NavBar';
// import Footer from './components/Footer';
import Header from "./components/Header"
import Home from "./components/Home"
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

class App extends Component {
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

    render() {
        return (
            <div className="flex-column full-height">
                <Header />
                <div className="main">
                    <Route exact path="/" component={Home} />
                    {/* <Route path='/:anything' render={() => this.renderMapView()}/> */}
                </div>
                {/* <Footer/> */}
            </div>
        )
    }
}

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

export default App
