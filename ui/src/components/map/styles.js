import {Box} from 'components/Grid'
import styled from 'style'

export const MapControlWrapper = styled(Box).attrs({
    p: '4px'
})`
z-index: 2000;
background-color: #fff;
    border: 1px solid #aaa;
    position: absolute;
    border-radius: 4px;
    box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);

    &:hover {
        background-color: #eee;
    }
`